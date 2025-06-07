import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import threading
import subprocess
from pathlib import Path

# Agregar el directorio actual al path para importar el módulo reporte_issues
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reporte_issues

class GithubReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Reportes de GitHub")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Variables
        self.github_token = tk.StringVar()
        self.repo = tk.StringVar()
        self.enable_pdf = tk.BooleanVar(value=False)
        self.output_dir = tk.StringVar(value=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reportes"))
        self.status_text = tk.StringVar(value="Listo para generar reportes...")
        
        # Intentar cargar valores del .env
        self.load_env_values()
        
        # Crear el diseño
        self.create_widgets()
        
    def load_env_values(self):
        """Cargar los valores del archivo .env si existe"""
        # Intentar cargar desde directorio actual y raíz
        env_loaded = False
        try:
            # Verificar en el directorio actual
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.strip() and '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == "GITHUB_TOKEN":
                                self.github_token.set(value)
                            elif key == "REPO":
                                self.repo.set(value)
                            elif key == "ENABLE_PDF" and value.lower() == "true":
                                self.enable_pdf.set(True)
                env_loaded = True
            
            # Si no se encontró en el directorio actual, buscar en el directorio raíz
            if not env_loaded:
                root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
                env_path = os.path.join(root_dir, ".env")
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.strip() and '=' in line:
                                key, value = line.strip().split('=', 1)
                                if key == "GITHUB_TOKEN":
                                    self.github_token.set(value)
                                elif key == "REPO":
                                    self.repo.set(value)
                                elif key == "ENABLE_PDF" and value.lower() == "true":
                                    self.enable_pdf.set(True)
        except Exception as e:
            print(f"Error al cargar archivo .env: {e}")
    
    def create_widgets(self):
        """Crear los elementos de la interfaz"""
        # Crear un notebook (pestañas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de configuración
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuración")
        
        # Pestaña de resultados
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Resultados")
        
        # Pestaña de ayuda
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text="Ayuda")
        
        # === Pestaña de Configuración ===
        config_frame.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(config_frame, text="Configuración del Reporte", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=10, sticky="w")
        
        # Token de GitHub
        ttk.Label(config_frame, text="Token de GitHub:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        token_entry = ttk.Entry(config_frame, textvariable=self.github_token, width=50, show="*")
        token_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(config_frame, text="Ver", command=lambda: self.toggle_password_visibility(token_entry)).grid(
            row=1, column=2, padx=5, pady=5)
        
        # Repositorio
        ttk.Label(config_frame, text="Repositorio:").grid(
            row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(config_frame, textvariable=self.repo, width=50).grid(
            row=2, column=1, padx=5, pady=5, sticky="we")
        ttk.Label(config_frame, text="(formato: usuario/repo)").grid(
            row=2, column=2, padx=5, pady=5, sticky="w")
        
        # Directorio de salida
        ttk.Label(config_frame, text="Directorio de reportes:").grid(
            row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(config_frame, textvariable=self.output_dir, width=50).grid(
            row=3, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(config_frame, text="Buscar", command=self.browse_output_dir).grid(
            row=3, column=2, padx=5, pady=5)
        
        # Opciones de reportes
        ttk.Label(config_frame, text="Opciones de reporte:", font=("Helvetica", 12, "bold")).grid(
            row=4, column=0, columnspan=3, pady=(15, 5), sticky="w")
        
        # Generar PDF
        ttk.Checkbutton(config_frame, text="Generar reporte en PDF", variable=self.enable_pdf).grid(
            row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Información sobre PDF
        pdf_info = ttk.LabelFrame(config_frame, text="Información de PDF")
        pdf_info.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="we")
        pdf_info.columnconfigure(0, weight=1)
        
        ttk.Label(pdf_info, text="Para generar PDFs se requiere tener instalado ReportLab:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(pdf_info, text="pip install reportlab markdown2").grid(
            row=1, column=0, padx=25, pady=5, sticky="w")
        
        # Botones de acción
        action_frame = ttk.Frame(config_frame)
        action_frame.grid(row=7, column=0, columnspan=3, pady=20, sticky="we")
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        ttk.Button(action_frame, text="Guardar Configuración", command=self.save_config).grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Button(action_frame, text="Generar Reportes", command=self.generate_reports).grid(
            row=0, column=1, padx=5, pady=5)
        
        # Barra de estado
        status_frame = ttk.Frame(config_frame)
        status_frame.grid(row=8, column=0, columnspan=3, sticky="we", pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        
        ttk.Label(status_frame, textvariable=self.status_text).grid(
            row=0, column=0, sticky="w", padx=5)
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky="we", padx=5, pady=5)
        
        # === Pestaña de Resultados ===
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        ttk.Label(results_frame, text="Resultados del último reporte generado:", font=("Helvetica", 14, "bold")).grid(
            row=0, column=0, pady=10, sticky="w")
        
        # Área de texto para mostrar resultados
        self.results_area = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20)
        self.results_area.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.results_area.config(state=tk.DISABLED)
        
        # Botones para abrir reportes
        btn_frame = ttk.Frame(results_frame)
        btn_frame.grid(row=2, column=0, pady=10, sticky="we")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        
        ttk.Button(btn_frame, text="Abrir Excel", command=lambda: self.open_file("excel")).grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Abrir Markdown", command=lambda: self.open_file("markdown")).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Abrir PDF", command=lambda: self.open_file("pdf")).grid(
            row=0, column=2, padx=5, pady=5)
        
        # === Pestaña de Ayuda ===
        help_frame.columnconfigure(0, weight=1)
        help_frame.rowconfigure(1, weight=1)
        
        ttk.Label(help_frame, text="Ayuda y Documentación", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, pady=10, sticky="w")
        
        # Contenido de ayuda
        help_text = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD)
        help_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        help_text.insert(tk.END, """# Generador de Reportes de GitHub

Este programa genera reportes detallados de issues y pull requests de un repositorio de GitHub.

## Cómo usar esta aplicación

1. En la pestaña "Configuración", ingrese su token de GitHub y el nombre del repositorio.
2. Seleccione si desea generar un reporte en PDF (requiere ReportLab).
3. Haga clic en "Generar Reportes".
4. Los reportes se guardarán en la carpeta "reportes" y se podrán abrir desde la pestaña "Resultados".

## Obtener un token de GitHub

1. Inicie sesión en GitHub.
2. Vaya a Configuración > Configuración de desarrollador > Tokens de acceso personal.
3. Haga clic en "Generar nuevo token".
4. Asigne un nombre al token y seleccione los permisos necesarios (al menos "repo").
5. Haga clic en "Generar token" y cópielo.

## Formato del repositorio

El repositorio debe especificarse en el formato "usuario/repositorio", por ejemplo:
- microsoft/vscode
- facebook/react
- tensorflow/tensorflow

## Problemas comunes

Si tiene problemas para generar PDFs, asegúrese de tener instaladas las dependencias:
```
pip install reportlab markdown2
```

Para más información, consulte el archivo README.md o REPORTLAB_INSTRUCCIONES.md.
""")
        help_text.config(state=tk.DISABLED)
    
    def toggle_password_visibility(self, entry):
        """Alternar entre mostrar y ocultar el token"""
        if entry.cget("show") == "*":
            entry.config(show="")
        else:
            entry.config(show="*")
    
    def browse_output_dir(self):
        """Abrir diálogo para seleccionar directorio de salida"""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir.get(),
            title="Seleccionar directorio para reportes"
        )
        if directory:
            self.output_dir.set(directory)
    
    def save_config(self):
        """Guardar la configuración en el archivo .env"""
        try:
            # Determinar la ubicación del archivo .env (raíz del proyecto)
            root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
            env_path = os.path.join(root_dir, ".env")
            
            with open(env_path, 'w') as f:
                f.write(f"GITHUB_TOKEN={self.github_token.get()}\n")
                f.write(f"REPO={self.repo.get()}\n")
                f.write(f"ENABLE_PDF={'true' if self.enable_pdf.get() else 'false'}\n")
            
            self.status_text.set("Configuración guardada correctamente.")
            messagebox.showinfo("Éxito", "Configuración guardada en archivo .env")
        except Exception as e:
            self.status_text.set(f"Error al guardar la configuración: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
    
    def generate_reports(self):
        """Generar los reportes en un hilo separado"""
        # Validar entradas
        if not self.github_token.get() or not self.repo.get():
            messagebox.showerror("Error", "Debe proporcionar un token de GitHub y un repositorio.")
            return
        
        # Establecer variables de entorno para el script
        os.environ["GITHUB_TOKEN"] = self.github_token.get()
        os.environ["REPO"] = self.repo.get()
        os.environ["ENABLE_PDF"] = "true" if self.enable_pdf.get() else "false"
        
        # Crear directorio de salida si no existe
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
        # Iniciar el progreso
        self.status_text.set("Generando reportes... Por favor espere.")
        self.progress.start()
        
        # Iniciar el proceso en un hilo separado
        thread = threading.Thread(target=self.run_report_generation)
        thread.daemon = True
        thread.start()
    
    def run_report_generation(self):
        """Ejecutar la generación de reportes"""
        try:
            # Obtener información
            self.root.after(0, lambda: self.update_status("Obteniendo issues y PRs..."))
            issues_y_prs = reporte_issues.obtener_issues_y_prs()
            
            self.root.after(0, lambda: self.update_status("Obteniendo commits..."))
            commits = reporte_issues.obtener_commits()
            
            self.root.after(0, lambda: self.update_status("Procesando datos..."))
            filas = reporte_issues.procesar_reporte(issues_y_prs, commits)
            
            # Generar reportes
            self.root.after(0, lambda: self.update_status("Generando Excel..."))
            reporte_issues.generar_excel(filas)
            
            self.root.after(0, lambda: self.update_status("Generando Markdown..."))
            reporte_issues.generar_markdown(filas)
            
            if self.enable_pdf.get():
                self.root.after(0, lambda: self.update_status("Generando PDF..."))
                pdf_generado = reporte_issues.generar_pdf_desde_markdown()
                if not pdf_generado:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Advertencia", 
                        "No se pudo generar el archivo PDF. Revise si tiene instalado ReportLab."
                    ))
            
            # Mostrar resultados
            self.root.after(0, lambda: self.show_results(len(issues_y_prs), filas))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(str(e)))
    
    def update_status(self, message):
        """Actualizar el mensaje de estado"""
        self.status_text.set(message)
    
    def handle_error(self, error_message):
        """Manejar errores en la generación de reportes"""
        self.progress.stop()
        self.status_text.set(f"Error: {error_message}")
        messagebox.showerror("Error", f"No se pudieron generar los reportes: {error_message}")
    
    def show_results(self, total_items, filas):
        """Mostrar los resultados de la generación"""
        self.progress.stop()
        self.status_text.set("Reportes generados correctamente.")
        
        # Actualizar el área de resultados
        self.results_area.config(state=tk.NORMAL)
        self.results_area.delete(1.0, tk.END)
        
        # Construir el resumen
        issues_abiertos = sum(1 for f in filas if f["Tipo"] == "Issue" and f["Estado"] == "open")
        issues_cerrados = sum(1 for f in filas if f["Tipo"] == "Issue" and f["Estado"] == "closed")
        prs_abiertos = sum(1 for f in filas if f["Tipo"] == "Pull Request" and f["Estado"] == "open")
        prs_cerrados = sum(1 for f in filas if f["Tipo"] == "Pull Request" and f["Estado"] == "closed")
        
        # Insertar resumen
        self.results_area.insert(tk.END, f"RESUMEN DEL REPOSITORIO: {self.repo.get()}\n")
        self.results_area.insert(tk.END, "="*50 + "\n\n")
        self.results_area.insert(tk.END, f"Total de elementos analizados: {total_items}\n\n")
        self.results_area.insert(tk.END, "ISSUES:\n")
        self.results_area.insert(tk.END, f"  - Abiertos: {issues_abiertos}\n")
        self.results_area.insert(tk.END, f"  - Cerrados: {issues_cerrados}\n")
        self.results_area.insert(tk.END, f"  - Total: {issues_abiertos + issues_cerrados}\n\n")
        self.results_area.insert(tk.END, "PULL REQUESTS:\n")
        self.results_area.insert(tk.END, f"  - Abiertos: {prs_abiertos}\n")
        self.results_area.insert(tk.END, f"  - Cerrados: {prs_cerrados}\n")
        self.results_area.insert(tk.END, f"  - Total: {prs_abiertos + prs_cerrados}\n\n")
        
        self.results_area.insert(tk.END, "ARCHIVOS GENERADOS:\n")
        self.results_area.insert(tk.END, f"  - Excel: {os.path.join(self.output_dir.get(), 'reporte_completo.xlsx')}\n")
        self.results_area.insert(tk.END, f"  - Markdown: {os.path.join(self.output_dir.get(), 'reporte_completo.md')}\n")
        if self.enable_pdf.get():
            self.results_area.insert(tk.END, f"  - PDF: {os.path.join(self.output_dir.get(), 'reporte_completo.pdf')}\n")
        
        self.results_area.config(state=tk.DISABLED)
        
        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", "Reportes generados correctamente.")
    
    def open_file(self, file_type):
        """Abrir un archivo de reporte"""
        try:
            if file_type == "excel":
                file_path = os.path.join(self.output_dir.get(), "reporte_completo.xlsx")
            elif file_type == "markdown":
                file_path = os.path.join(self.output_dir.get(), "reporte_completo.md")
            else:  # pdf
                file_path = os.path.join(self.output_dir.get(), "reporte_completo.pdf")
            
            if os.path.exists(file_path):
                if sys.platform == "win32":
                    os.startfile(file_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
            else:
                messagebox.showerror("Error", f"El archivo {file_path} no existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GithubReportApp(root)
    root.mainloop()
