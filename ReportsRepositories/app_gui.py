import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import sys
import threading
from pathlib import Path
import subprocess
from datetime import datetime, timedelta
import numpy as np
import reporte_issues
from analytics import GitHubAnalytics

ctk.set_appearance_mode("system")  # Puede ser "dark", "light" o "system"
ctk.set_default_color_theme("blue")


class GithubReportApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Reportes de GitHub")
        self.geometry("900x650")
        self.minsize(900, 650)
        self.iconbitmap(default=None)

        # Variables
        self.github_token = ctk.StringVar()
        self.repo = ctk.StringVar()
        self.enable_pdf = ctk.BooleanVar(value=False)
        self.output_dir = ctk.StringVar(
            value=os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                "..",
                "reportes"))
        self.status_text = ctk.StringVar(
            value="Listo para generar reportes...")

        # Variables para filtros
        self.fecha_inicio = ctk.StringVar()
        self.fecha_fin = ctk.StringVar()
        self.filtro_autor = ctk.StringVar()
        self.filtro_etiqueta = ctk.StringVar()
        self.filtro_estado = ctk.StringVar(value="Todos")
        self.filtro_tipo = ctk.StringVar(value="Todos")
        self.busqueda_texto = ctk.StringVar()
        # Datos para análisis
        self.datos_actuales = []
        self.analytics = None

        self.load_env_values()
        self.create_widgets()

    def load_env_values(self):
        env_loaded = False
        try:
            env_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                ".env")
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
            if not env_loaded:
                root_dir = Path(
                    os.path.dirname(
                        os.path.abspath(__file__))).parent
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
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.config_tab = self.tabview.add("Configuración")
        self.analytics_tab = self.tabview.add("📊 Analytics")
        self.filters_tab = self.tabview.add("🔍 Filtros")
        self.results_tab = self.tabview.add("Resultados")
        self.help_tab = self.tabview.add("Ayuda")

        self.create_config_tab()
        self.create_analytics_tab()
        self.create_filters_tab()
        self.create_results_tab()
        self.create_help_tab()

    def create_config_tab(self):
        # --- Configuración ---
        ctk.CTkLabel(
            self.config_tab,
            text="Configuración del Reporte",
            font=(
                "Segoe UI",
                22,
                "bold")).pack(
            pady=(
                10,
                20))
        form = ctk.CTkFrame(self.config_tab, fg_color=("#f5f6fa", "#222831"))
        form.pack(padx=30, pady=10, fill="x")

        # Token
        ctk.CTkLabel(
            form,
            text="Token de GitHub:",
            anchor="w").grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="w")
        self.token_entry = ctk.CTkEntry(
            form, textvariable=self.github_token, width=350, show="*")
        self.token_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.show_token_btn = ctk.CTkButton(
            form, text="👁", width=40, command=self.toggle_password_visibility)
        self.show_token_btn.grid(row=0, column=2, padx=5, pady=10)

        # Repo
        ctk.CTkLabel(
            form,
            text="Repositorio:",
            anchor="w").grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="w")
        ctk.CTkEntry(
            form,
            textvariable=self.repo,
            width=350).grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="w")
        ctk.CTkLabel(form, text="(usuario/repo)").grid(row=1,
                                                       column=2, padx=5, pady=10, sticky="w")

        # Output dir
        ctk.CTkLabel(
            form,
            text="Directorio de reportes:",
            anchor="w").grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
            sticky="w")
        ctk.CTkEntry(
            form,
            textvariable=self.output_dir,
            width=350).grid(
            row=2,
            column=1,
            padx=10,
            pady=10,
            sticky="w")
        ctk.CTkButton(
            form,
            text="Buscar",
            command=self.browse_output_dir,
            width=80).grid(
            row=2,
            column=2,
            padx=5,
            pady=10)

        # PDF option
        ctk.CTkCheckBox(
            form,
            text="Generar reporte en PDF",
            variable=self.enable_pdf).grid(
            row=3,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="w")
        ctk.CTkLabel(
            form,
            text="Para PDF: pip install reportlab markdown2",
            text_color="#888").grid(
            row=3,
            column=2,
            padx=5,
            pady=10,
            sticky="w")

        # Botones acción
        btns = ctk.CTkFrame(self.config_tab, fg_color="transparent")
        btns.pack(pady=20)
        ctk.CTkButton(
            btns,
            text="Guardar Configuración",
            command=self.save_config,
            fg_color="#0078D4",
            hover_color="#005fa3").pack(
            side="left",
            padx=10)
        ctk.CTkButton(
            btns,
            text="Generar Reportes",
            command=self.generate_reports,
            fg_color="#43a047",
            hover_color="#357a38").pack(
            side="left",
            padx=10)

        # Estado
        status = ctk.CTkFrame(self.config_tab, fg_color="transparent")
        status.pack(fill="x", pady=(10, 0), padx=30)
        ctk.CTkLabel(
            status,
            textvariable=self.status_text,
            text_color="#0078D4").pack(
            side="left",
            padx=5)
        self.progress = ctk.CTkProgressBar(status, orientation="horizontal")
        self.progress.pack(side="right", fill="x", expand=True, padx=5)
        self.progress.set(0)

    def create_analytics_tab(self):
        """Crear la pestaña de analytics con dashboard interactivo"""
        ctk.CTkLabel(
            self.analytics_tab,
            text="📊 Dashboard de Analytics",
            font=(
                "Segoe UI",
                22,
                "bold")).pack(
            pady=(
                10,
                20))

        # Botones de control
        control_frame = ctk.CTkFrame(self.analytics_tab)
        control_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            control_frame,
            text="🔄 Cargar Datos",
            command=self.load_analytics_data,
            fg_color="#0078D4",
            hover_color="#005fa3").pack(
            side="left",
            padx=10,
            pady=10)
        ctk.CTkButton(
            control_frame,
            text="📈 Generar Dashboard",
            command=self.generate_dashboard,
            fg_color="#43a047",
            hover_color="#357a38").pack(
            side="left",
            padx=10,
            pady=10)
        ctk.CTkButton(
            control_frame,
            text="🌐 Abrir Dashboard",
            command=self.open_dashboard,
            fg_color="#ff9800",
            hover_color="#f57c00").pack(
            side="left",
            padx=10,
            pady=10)

        # Área de estadísticas rápidas
        stats_frame = ctk.CTkFrame(self.analytics_tab)
        stats_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            stats_frame,
            text="📊 Estadísticas Rápidas",
            font=(
                "Segoe UI",
                16,
                "bold")).pack(
            pady=10)

        # Grid de estadísticas
        stats_grid = ctk.CTkFrame(stats_frame)
        stats_grid.pack(fill="x", padx=10, pady=10)

        # Variables para estadísticas
        self.total_issues_var = ctk.StringVar(value="0")
        self.total_prs_var = ctk.StringVar(value="0")
        self.active_contributors_var = ctk.StringVar(value="0")
        self.avg_resolution_time_var = ctk.StringVar(value="0 días")

        # Estadísticas en grid
        ctk.CTkLabel(
            stats_grid,
            text="Total Issues:",
            font=(
                "Segoe UI",
                12,
                "bold")).grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkLabel(
            stats_grid,
            textvariable=self.total_issues_var,
            text_color="#e53935").grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="w")

        ctk.CTkLabel(
            stats_grid,
            text="Total PRs:",
            font=(
                "Segoe UI",
                12,
                "bold")).grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkLabel(
            stats_grid,
            textvariable=self.total_prs_var,
            text_color="#43a047").grid(
            row=0,
            column=3,
            padx=10,
            pady=5,
            sticky="w")

        ctk.CTkLabel(
            stats_grid,
            text="Contribuyentes Activos:",
            font=(
                "Segoe UI",
                12,
                "bold")).grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkLabel(
            stats_grid,
            textvariable=self.active_contributors_var,
            text_color="#0078D4").grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="w")

        ctk.CTkLabel(
            stats_grid,
            text="Tiempo Promedio de Resolución:",
            font=(
                "Segoe UI",
                12,
                "bold")).grid(
            row=1,
            column=2,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkLabel(
            stats_grid,
            textvariable=self.avg_resolution_time_var,
            text_color="#ff9800").grid(
            row=1,
            column=3,
            padx=10,
            pady=5,
            sticky="w")

        # Área de información
        self.analytics_info = ctk.CTkTextbox(
            self.analytics_tab, height=200, font=(
                "Segoe UI", 12))
        self.analytics_info.pack(fill="both", expand=True, padx=20, pady=10)
        self.analytics_info.insert("0.0", "💡 Información de Analytics\n\n")
        self.analytics_info.insert(
            "end", "1. Haga clic en 'Cargar Datos' para cargar los datos del repositorio\n")
        self.analytics_info.insert(
            "end", "2. Use 'Generar Dashboard' para crear visualizaciones interactivas\n")
        self.analytics_info.insert(
            "end", "3. Abra el dashboard en su navegador con 'Abrir Dashboard'\n\n")
        self.analytics_info.insert("end", "📈 El dashboard incluye:\n")
        self.analytics_info.insert(
            "end", "• Análisis de tendencias temporales\n")
        self.analytics_info.insert(
            "end", "• Gráficos de contribuyentes activos\n")
        self.analytics_info.insert(
            "end", "• Distribución de tiempos de resolución\n")
        self.analytics_info.insert(
            "end", "• Visualización de etiquetas populares\n")
        self.analytics_info.insert(
            "end", "• Análisis de estados de issues y PRs\n")
        self.analytics_info.configure(state="disabled")

    def create_filters_tab(self):
        """Crear la pestaña de filtros avanzados"""
        ctk.CTkLabel(
            self.filters_tab,
            text="🔍 Filtros Avanzados",
            font=(
                "Segoe UI",
                22,
                "bold")).pack(
            pady=(
                10,
                20))

        # Frame principal de filtros
        main_filter_frame = ctk.CTkFrame(self.filters_tab)
        main_filter_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Filtros de fecha
        date_frame = ctk.CTkFrame(main_filter_frame)
        date_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            date_frame,
            text="📅 Filtros de Fecha",
            font=(
                "Segoe UI",
                16,
                "bold")).pack(
            pady=(
                10,
                5))

        date_grid = ctk.CTkFrame(date_frame)
        date_grid.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            date_grid,
            text="Fecha Inicio:").grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkEntry(
            date_grid,
            textvariable=self.fecha_inicio,
            placeholder_text="YYYY-MM-DD",
            width=150).grid(
            row=0,
            column=1,
            padx=10,
            pady=5)

        ctk.CTkLabel(
            date_grid,
            text="Fecha Fin:").grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkEntry(
            date_grid,
            textvariable=self.fecha_fin,
            placeholder_text="YYYY-MM-DD",
            width=150).grid(
            row=0,
            column=3,
            padx=10,
            pady=5)

        # Botones de fecha predefinidos
        date_buttons = ctk.CTkFrame(date_frame)
        date_buttons.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            date_buttons,
            text="🗓️ Último Mes",
            command=lambda: self.set_date_filter(30),
            width=100).pack(
            side="left",
            padx=5)
        ctk.CTkButton(
            date_buttons,
            text="📆 Últimos 3 Meses",
            command=lambda: self.set_date_filter(90),
            width=120).pack(
            side="left",
            padx=5)
        ctk.CTkButton(
            date_buttons,
            text="📅 Último Año",
            command=lambda: self.set_date_filter(365),
            width=100).pack(
            side="left",
            padx=5)
        ctk.CTkButton(
            date_buttons,
            text="🔄 Limpiar",
            command=self.clear_date_filters,
            width=80).pack(
            side="left",
            padx=5)

        # Filtros de contenido
        content_frame = ctk.CTkFrame(main_filter_frame)
        content_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            content_frame,
            text="📝 Filtros de Contenido",
            font=(
                "Segoe UI",
                16,
                "bold")).pack(
            pady=(
                10,
                5))

        content_grid = ctk.CTkFrame(content_frame)
        content_grid.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            content_grid,
            text="Autor:").grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkEntry(
            content_grid,
            textvariable=self.filtro_autor,
            placeholder_text="nombre_usuario",
            width=150).grid(
            row=0,
            column=1,
            padx=10,
            pady=5)

        ctk.CTkLabel(
            content_grid,
            text="Etiqueta:").grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkEntry(
            content_grid,
            textvariable=self.filtro_etiqueta,
            placeholder_text="bug, feature, etc.",
            width=150).grid(
            row=0,
            column=3,
            padx=10,
            pady=5)

        ctk.CTkLabel(
            content_grid,
            text="Estado:").grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkComboBox(
            content_grid,
            variable=self.filtro_estado,
            values=[
                "Todos",
                "open",
                "closed"],
            width=150).grid(
            row=1,
            column=1,
            padx=10,
            pady=5)

        ctk.CTkLabel(
            content_grid,
            text="Tipo:").grid(
            row=1,
            column=2,
            padx=10,
            pady=5,
            sticky="w")
        ctk.CTkComboBox(
            content_grid,
            variable=self.filtro_tipo,
            values=[
                "Todos",
                "Issue",
                "Pull Request"],
            width=150).grid(
            row=1,
            column=3,
            padx=10,
            pady=5)

        # Búsqueda de texto
        search_frame = ctk.CTkFrame(content_frame)
        search_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="🔍 Búsqueda en Texto:").pack(
            side="left",
            padx=10)
        ctk.CTkEntry(
            search_frame,
            textvariable=self.busqueda_texto,
            placeholder_text="Buscar en títulos y descripción...",
            width=300).pack(
            side="left",
            padx=10)

        # Botones de acción
        action_frame = ctk.CTkFrame(main_filter_frame)
        action_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkButton(
            action_frame,
            text="🔍 Aplicar Filtros",
            command=self.apply_filters,
            fg_color="#0078D4",
            hover_color="#005fa3").pack(
            side="left",
            padx=10)
        ctk.CTkButton(
            action_frame,
            text="🧹 Limpiar Filtros",
            command=self.clear_filters,
            fg_color="#6c757d",
            hover_color="#5a6268").pack(
            side="left",
            padx=10)
        ctk.CTkButton(
            action_frame,
            text="💾 Exportar Datos Filtrados",
            command=self.export_filtered_data,
            fg_color="#28a745",
            hover_color="#218838").pack(
            side="left",
            padx=10)

        # Área de resultados de filtros
        results_filter_frame = ctk.CTkFrame(main_filter_frame)
        results_filter_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            results_filter_frame,
            text="📊 Resultados de Filtros",
            font=(
                "Segoe UI",
                16,
                "bold")).pack(
            pady=10)

        self.filter_results = ctk.CTkTextbox(
            results_filter_frame, height=150, font=(
                "Segoe UI", 12))
        self.filter_results.pack(fill="both", expand=True, padx=10, pady=10)
        self.filter_results.insert(
            "0.0", "Los resultados de los filtros aplicados aparecerán aquí.\n\n")
        self.filter_results.insert(
            "end",
            "Use los controles superiores para configurar filtros y haga clic en 'Aplicar Filtros'.")
        self.filter_results.configure(state="disabled")

    def create_results_tab(self):
        """Crear la pestaña de resultados mejorada"""
        ctk.CTkLabel(
            self.results_tab,
            text="📈 Resultados y Análisis",
            font=(
                "Segoe UI",
                18,
                "bold")).pack(
            pady=10,
            anchor="w")

        # Área de resultados principal
        self.results_area = ctk.CTkTextbox(
            self.results_tab, height=350, font=(
                "Consolas", 13), wrap="word")
        self.results_area.pack(fill="both", expand=True, padx=20, pady=10)
        self.results_area.configure(state="disabled")

        # Botones de acción
        btns2 = ctk.CTkFrame(self.results_tab, fg_color="transparent")
        btns2.pack(pady=10)

        ctk.CTkButton(
            btns2,
            text="📊 Abrir Excel",
            command=lambda: self.open_file("excel"),
            fg_color="#0078D4").pack(
            side="left",
            padx=10)
        ctk.CTkButton(
            btns2,
            text="📝 Abrir Markdown",
            command=lambda: self.open_file("markdown"),
            fg_color="#6d4aff").pack(
            side="left",
            padx=10)
        ctk.CTkButton(
            btns2,
            text="📄 Abrir PDF",
            command=lambda: self.open_file("pdf"),
            fg_color="#e53935").pack(
            side="left",
            padx=10)
        ctk.CTkButton(
            btns2,
            text="📈 Ver Dashboard",
            command=self.open_dashboard,
            fg_color="#ff9800").pack(
            side="left",
            padx=10)

    def create_help_tab(self):
        """Crear la pestaña de ayuda"""
        ctk.CTkLabel(
            self.help_tab,
            text="Ayuda y Documentación",
            font=(
                "Segoe UI",
                20,
                "bold")).pack(
            pady=10,
            anchor="w")
        ayuda = ctk.CTkTextbox(
            self.help_tab, font=(
                "Segoe UI", 13), wrap="word")
        ayuda.pack(fill="both", expand=True, padx=20, pady=10)
        ayuda.insert("0.0", """# Generador de Reportes de GitHub

Este programa genera reportes detallados de issues y pull requests de un repositorio de GitHub con análisis avanzados.

## 🚀 Cómo usar esta aplicación

### Pestaña Configuración
1. Ingrese su token de GitHub y el nombre del repositorio
2. Seleccione si desea generar un reporte en PDF
3. Haga clic en 'Generar Reportes'

### Pestaña Analytics 📊
1. Haga clic en 'Cargar Datos' para obtener información del repositorio
2. Use 'Generar Dashboard' para crear visualizaciones interactivas
3. Abra el dashboard en su navegador con 'Abrir Dashboard'

El dashboard incluye:
• Análisis de tendencias temporales
• Gráficos de contribuyentes activos
• Distribución de tiempos de resolución
• Visualización de etiquetas populares
• Análisis de estados de issues y PRs

### Pestaña Filtros 🔍
1. Configure filtros por fecha, autor, etiquetas, estado o tipo
2. Use la búsqueda de texto para encontrar elementos específicos
3. Aplique filtros y vea estadísticas de los datos filtrados
4. Exporte los datos filtrados a Excel

### Pestaña Resultados 📈
- Vea resúmenes de los reportes generados
- Abra archivos Excel, Markdown y PDF
- Acceda al dashboard de analytics

## 🔑 Obtener un token de GitHub

1. Inicie sesión en GitHub
2. Vaya a Configuración > Configuración de desarrollador > Tokens de acceso personal
3. Haga clic en 'Generate new token (classic)'
4. Asigne un nombre al token y seleccione los permisos 'repo'
5. Genere el token y cópielo

## 📋 Formato del repositorio

Especifique el repositorio como 'usuario/repositorio':
- microsoft/vscode
- facebook/react
- tensorflow/tensorflow

## 🛠️ Problemas comunes

### Para PDFs:
pip install reportlab markdown2

### Para Analytics:
pip install matplotlib seaborn plotly numpy

### Si tiene problemas con CustomTkinter:
pip install customtkinter

## 📊 Funciones de Analytics

- **Tendencias**: Análisis temporal de issues y PRs
- **Contribuyentes**: Identificación de usuarios más activos
- **Tiempos**: Análisis de tiempo de resolución
- **Etiquetas**: Visualización de tags más utilizados
- **Estados**: Distribución de elementos abiertos/cerrados
- **Filtros**: Sistema avanzado de filtrado
- **Exportación**: Datos en formato Excel para análisis externo

Para más información, consulte README.md o REPORTLAB_INSTRUCCIONES.md.
""")
        ayuda.configure(state="disabled")

    # Nuevos métodos para Analytics y Filtros
    def load_analytics_data(self):
        """Cargar datos para análisis"""
        if not self.github_token.get() or not self.repo.get():
            messagebox.showerror(
                "Error", "Debe configurar el token y repositorio primero.")
            return

        try:
            self.status_text.set("Cargando datos para análisis...")
            self.progress.set(0.1)

            # Configurar variables de entorno
            os.environ["GITHUB_TOKEN"] = self.github_token.get()
            os.environ["REPO"] = self.repo.get()

            # Obtener datos
            issues_y_prs = reporte_issues.obtener_issues_y_prs()
            commits = reporte_issues.obtener_commits()
            self.datos_actuales = reporte_issues.procesar_reporte(
                issues_y_prs, commits)

            # Inicializar analytics
            self.analytics = GitHubAnalytics(self.datos_actuales)

            # Actualizar estadísticas
            self.update_quick_stats()

            self.status_text.set("Datos cargados correctamente para análisis.")
            self.progress.set(1.0)

            # Actualizar área de información
            self.analytics_info.configure(state="normal")
            self.analytics_info.delete("0.0", "end")
            self.analytics_info.insert(
                "0.0", f"✅ Datos cargados exitosamente!\n\n")
            self.analytics_info.insert(
                "end", f"📊 Repositorio: {
                    self.repo.get()}\n")
            self.analytics_info.insert(
                "end", f"📈 Total de elementos: {len(self.datos_actuales)}\n")
            self.analytics_info.insert(
                "end", f"🗓️ Datos cargados: {
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            self.analytics_info.insert("end", "🎯 Ahora puede:\n")
            self.analytics_info.insert(
                "end", "• Generar dashboard interactivo\n")
            self.analytics_info.insert("end", "• Aplicar filtros avanzados\n")
            self.analytics_info.insert("end", "• Exportar datos filtrados\n")
            self.analytics_info.configure(state="disabled")

        except Exception as e:
            self.status_text.set(f"Error al cargar datos: {e}")
            self.progress.set(0)
            messagebox.showerror(
                "Error", f"No se pudieron cargar los datos: {e}")

    def update_quick_stats(self):
        """Actualizar estadísticas rápidas"""
        if not self.datos_actuales:
            return

        issues = [d for d in self.datos_actuales if d.get("Tipo") == "Issue"]
        prs = [d for d in self.datos_actuales if d.get(
            "Tipo") == "Pull Request"]

        # Contar contribuyentes únicos
        autores = set()
        for item in self.datos_actuales:
            if item.get("Autor"):
                autores.add(item["Autor"])

        # Calcular tiempo promedio de resolución
        tiempos_resolucion = []
        for item in self.datos_actuales:
            if item.get("Estado") == "closed" and item.get(
                    "Fecha_Cerrado") and item.get("Fecha_Creacion"):
                try:
                    creado = datetime.fromisoformat(
                        item["Fecha_Creacion"].replace('Z', '+00:00'))
                    cerrado = datetime.fromisoformat(
                        item["Fecha_Cerrado"].replace('Z', '+00:00'))
                    dias = (cerrado - creado).days
                    if dias >= 0:
                        tiempos_resolucion.append(dias)
                except BaseException:
                    continue

        avg_resolution = np.mean(
            tiempos_resolucion) if tiempos_resolucion else 0

        # Actualizar variables
        self.total_issues_var.set(str(len(issues)))
        self.total_prs_var.set(str(len(prs)))
        self.active_contributors_var.set(str(len(autores)))
        self.avg_resolution_time_var.set(f"{avg_resolution:.1f} días")

    def generate_dashboard(self):
        """Generar dashboard interactivo"""
        if not self.analytics or not self.datos_actuales:
            messagebox.showwarning(
                "Advertencia", "Debe cargar los datos primero.")
            return

        try:
            self.status_text.set("Generando dashboard...")
            self.progress.set(0.5)

            # Generar dashboard
            dashboard_path = self.analytics.generate_dashboard(
                self.datos_actuales,
                self.output_dir.get(),
                self.repo.get()
            )

            self.status_text.set("Dashboard generado correctamente.")
            self.progress.set(1.0)

            messagebox.showinfo(
                "Éxito", f"Dashboard generado en: {dashboard_path}")

        except Exception as e:
            self.status_text.set(f"Error al generar dashboard: {e}")
            self.progress.set(0)
            messagebox.showerror(
                "Error", f"No se pudo generar el dashboard: {e}")

    def open_dashboard(self):
        """Abrir dashboard en el navegador"""
        dashboard_path = os.path.join(
            self.output_dir.get(),
            "github_analytics_dashboard.html")

        if os.path.exists(dashboard_path):
            try:
                if sys.platform == "win32":
                    os.startfile(dashboard_path)
                elif sys.platform == "darwin":
                    os.system(f"open '{dashboard_path}'")
                else:
                    os.system(f"xdg-open '{dashboard_path}'")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo abrir el dashboard: {e}")
        else:
            messagebox.showwarning("Advertencia",
                                   "Dashboard no encontrado. Genérelo primero.")

    # === MÉTODOS PARA FILTROS ===

    def set_date_filter(self, days_back):
        """Establecer filtros de fecha predefinidos"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        self.fecha_inicio.set(start_date.strftime("%Y-%m-%d"))
        self.fecha_fin.set(end_date.strftime("%Y-%m-%d"))

    def clear_date_filters(self):
        """Limpiar filtros de fecha"""
        self.fecha_inicio.set("")
        self.fecha_fin.set("")

    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.fecha_inicio.set("")
        self.fecha_fin.set("")
        self.filtro_autor.set("")
        self.filtro_etiqueta.set("")
        self.filtro_estado.set("Todos")
        self.filtro_tipo.set("Todos")
        self.busqueda_texto.set("")

        self.filter_results.configure(state="normal")
        self.filter_results.delete("0.0", "end")
        self.filter_results.insert(
            "0.0",
            "Filtros limpiados. Configure nuevos filtros y haga clic en 'Aplicar Filtros'.")
        self.filter_results.configure(state="disabled")

    def apply_filters(self):
        """Aplicar filtros a los datos"""
        if not self.analytics or not self.datos_actuales:
            messagebox.showwarning(
                "Advertencia", "Debe cargar los datos primero.")
            return

        try:
            # Construir filtros
            filters = {}

            if self.fecha_inicio.get():
                filters['start_date'] = self.fecha_inicio.get()
            if self.fecha_fin.get():
                filters['end_date'] = self.fecha_fin.get()
            if self.filtro_autor.get():
                filters['author'] = self.filtro_autor.get()
            if self.filtro_etiqueta.get():
                filters['labels'] = self.filtro_etiqueta.get()
            if self.filtro_estado.get() != "Todos":
                filters['state'] = self.filtro_estado.get()
            if self.filtro_tipo.get() != "Todos":
                filters['item_type'] = self.filtro_tipo.get()
            if self.busqueda_texto.get():
                filters['search_text'] = self.busqueda_texto.get()

            # Aplicar filtros
            filtered_data = self.analytics.filter_data(
                self.datos_actuales, filters)

            # Mostrar resultados
            self.show_filter_results(filtered_data, filters)

        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {e}")

    def show_filter_results(self, filtered_data, filters):
        """Mostrar resultados de filtros"""
        self.filter_results.configure(state="normal")
        self.filter_results.delete("0.0", "end")

        self.filter_results.insert("0.0", f"📊 Resultados de Filtros\n")
        self.filter_results.insert("end", "=" * 50 + "\n\n")

        # Mostrar filtros aplicados
        self.filter_results.insert("end", "🔍 Filtros aplicados:\n")
        for key, value in filters.items():
            filter_names = {
                'start_date': 'Fecha inicio',
                'end_date': 'Fecha fin',
                'author': 'Autor',
                'labels': 'Etiquetas',
                'state': 'Estado',
                'item_type': 'Tipo',
                'search_text': 'Búsqueda de texto'
            }
            self.filter_results.insert(
                "end", f"  • {
                    filter_names.get(
                        key, key)}: {value}\n")

        self.filter_results.insert(
            "end", f"\n📈 Resultados encontrados: {
                len(filtered_data)}\n\n")

        if filtered_data:
            # Estadísticas de los datos filtrados
            issues = [d for d in filtered_data if d.get("Tipo") == "Issue"]
            prs = [d for d in filtered_data if d.get("Tipo") == "Pull Request"]

            abiertos = [d for d in filtered_data if d.get("Estado") == "open"]
            cerrados = [
                d for d in filtered_data if d.get("Estado") == "closed"]

            self.filter_results.insert("end", "📊 Distribución por tipo:\n")
            self.filter_results.insert("end", f"  • Issues: {len(issues)}\n")
            self.filter_results.insert(
                "end", f"  • Pull Requests: {
                    len(prs)}\n\n")

            self.filter_results.insert("end", "📊 Distribución por estado:\n")
            self.filter_results.insert(
                "end", f"  • Abiertos: {
                    len(abiertos)}\n")
            self.filter_results.insert(
                "end", f"  • Cerrados: {
                    len(cerrados)}\n\n")

            # Autores más activos
            autores = {}
            for item in filtered_data:
                autor = item.get("Autor", "Desconocido")
                autores[autor] = autores.get(autor, 0) + 1

            top_autores = sorted(
                autores.items(),
                key=lambda x: x[1],
                reverse=True)[
                :5]

            self.filter_results.insert("end", "👥 Top 5 autores:\n")
            for autor, count in top_autores:
                self.filter_results.insert(
                    "end", f"  • {autor}: {count} elementos\n")
        else:
            self.filter_results.insert(
                "end", "❌ No se encontraron datos que coincidan con los filtros aplicados.\n")

        self.filter_results.configure(state="disabled")

    def export_filtered_data(self):
        """Exportar datos filtrados"""
        if not self.analytics or not self.datos_actuales:
            messagebox.showwarning(
                "Advertencia", "Debe cargar los datos primero.")
            return

        # Aplicar filtros actuales
        filters = {}
        if self.fecha_inicio.get():
            filters['start_date'] = self.fecha_inicio.get()
        if self.fecha_fin.get():
            filters['end_date'] = self.fecha_fin.get()
        if self.filtro_autor.get():
            filters['author'] = self.filtro_autor.get()
        if self.filtro_etiqueta.get():
            filters['labels'] = self.filtro_etiqueta.get()
        if self.filtro_estado.get() != "Todos":
            filters['state'] = self.filtro_estado.get()
        if self.filtro_tipo.get() != "Todos":
            filters['item_type'] = self.filtro_tipo.get()
        if self.busqueda_texto.get():
            filters['search_text'] = self.busqueda_texto.get()

        try:
            filtered_data = self.analytics.filter_data(
                self.datos_actuales, filters)

            if not filtered_data:
                messagebox.showwarning(
                    "Advertencia", "No hay datos filtrados para exportar.")
                return

            export_path = self.analytics.export_filtered_data(
                filtered_data, self.output_dir.get())

            messagebox.showinfo("Éxito", f"Datos exportados a: {export_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos: {e}")

    def toggle_password_visibility(self):
        if self.token_entry.cget("show") == "*":
            self.token_entry.configure(show="")
        else:
            self.token_entry.configure(show="*")

    def browse_output_dir(self):
        directory = filedialog.askdirectory(
            initialdir=self.output_dir.get(),
            title="Seleccionar directorio para reportes")
        if directory:
            self.output_dir.set(directory)

    def save_config(self):
        try:
            root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
            env_path = os.path.join(root_dir, ".env")
            with open(env_path, 'w') as f:
                f.write(f"GITHUB_TOKEN={self.github_token.get()}\n")
                f.write(f"REPO={self.repo.get()}\n")
                f.write(
                    f"ENABLE_PDF={
                        'true' if self.enable_pdf.get() else 'false'}\n")
            self.status_text.set("Configuración guardada correctamente.")
            messagebox.showinfo(
                "Éxito", "Configuración guardada en archivo .env")
        except Exception as e:
            self.status_text.set(f"Error al guardar la configuración: {e}")
            messagebox.showerror(
                "Error", f"No se pudo guardar la configuración: {e}")

    def generate_reports(self):
        if not self.github_token.get() or not self.repo.get():
            messagebox.showerror(
                "Error", "Debe proporcionar un token de GitHub y un repositorio.")
            return
        os.environ["GITHUB_TOKEN"] = self.github_token.get()
        os.environ["REPO"] = self.repo.get()
        os.environ["ENABLE_PDF"] = "true" if self.enable_pdf.get() else "false"
        os.makedirs(self.output_dir.get(), exist_ok=True)
        self.status_text.set("Generando reportes... Por favor espere.")
        self.progress.set(0.2)
        thread = threading.Thread(target=self.run_report_generation)
        thread.daemon = True
        thread.start()

    def run_report_generation(self):
        try:
            self.after(0, lambda: self.update_status(
                "Obteniendo issues y PRs..."))
            issues_y_prs = reporte_issues.obtener_issues_y_prs()
            self.after(0, lambda: self.update_status("Obteniendo commits..."))
            commits = reporte_issues.obtener_commits()
            self.after(0, lambda: self.update_status("Procesando datos..."))
            filas = reporte_issues.procesar_reporte(issues_y_prs, commits)

            # Guardar datos para analytics
            self.datos_actuales = filas

            self.after(0, lambda: self.update_status("Generando Excel..."))
            reporte_issues.generar_excel(filas)
            self.after(0, lambda: self.update_status("Generando Markdown..."))
            reporte_issues.generar_markdown(filas)
            if self.enable_pdf.get():
                self.after(0, lambda: self.update_status("Generando PDF..."))
                pdf_generado = reporte_issues.generar_pdf_desde_markdown(
                    self.datos_actuales)
                if not pdf_generado:
                    self.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Advertencia",
                            "No se pudo generar el archivo PDF. Revise si tiene instalado ReportLab."))

            # Generar analytics automáticamente si está disponible
            if not self.analytics:
                self.analytics = GitHubAnalytics()

            self.after(0, lambda: self.show_results(len(issues_y_prs), filas))
        except Exception as e:
            self.after(0, lambda: self.handle_error(str(e)))

    def update_status(self, message):
        self.status_text.set(message)
        self.progress.set(min(self.progress.get() + 0.2, 1.0))

    def handle_error(self, error_message):
        self.progress.set(0)
        self.status_text.set(f"Error: {error_message}")
        messagebox.showerror(
            "Error", f"No se pudieron generar los reportes: {error_message}")

    def show_results(self, total_items, filas):
        self.progress.set(1.0)
        self.status_text.set("Reportes generados correctamente.")
        self.results_area.configure(state="normal")
        self.results_area.delete("0.0", "end")
        issues_abiertos = sum(
            1 for f in filas if f["Tipo"] == "Issue" and f["Estado"] == "open")
        issues_cerrados = sum(
            1 for f in filas if f["Tipo"] == "Issue" and f["Estado"] == "closed")
        prs_abiertos = sum(
            1 for f in filas if f["Tipo"] == "Pull Request" and f["Estado"] == "open")
        prs_cerrados = sum(
            1 for f in filas if f["Tipo"] == "Pull Request" and f["Estado"] == "closed")
        self.results_area.insert(
            "end", f"RESUMEN DEL REPOSITORIO: {
                self.repo.get()}\n")
        self.results_area.insert("end", "=" * 50 + "\n\n")
        self.results_area.insert(
            "end", f"Total de elementos analizados: {total_items}\n\n")
        self.results_area.insert("end", "ISSUES:\n")
        self.results_area.insert("end", f"  - Abiertos: {issues_abiertos}\n")
        self.results_area.insert("end", f"  - Cerrados: {issues_cerrados}\n")
        self.results_area.insert(
            "end", f"  - Total: {issues_abiertos + issues_cerrados}\n\n")
        self.results_area.insert("end", "PULL REQUESTS:\n")
        self.results_area.insert("end", f"  - Abiertos: {prs_abiertos}\n")
        self.results_area.insert("end", f"  - Cerrados: {prs_cerrados}\n")
        self.results_area.insert(
            "end", f"  - Total: {prs_abiertos + prs_cerrados}\n\n")
        self.results_area.insert("end", "ARCHIVOS GENERADOS:\n")
        self.results_area.insert("end",
                                 f"  - Excel: {os.path.join(self.output_dir.get(),
                                                            'reporte_completo.xlsx')}\n")
        self.results_area.insert(
            "end", f"  - Markdown: {os.path.join(self.output_dir.get(), 'reporte_completo.md')}\n")
        if self.enable_pdf.get():
            self.results_area.insert(
                "end", f"  - PDF: {os.path.join(self.output_dir.get(), 'reporte_completo.pdf')}\n")
        self.results_area.configure(state="disabled")
        messagebox.showinfo("Éxito", "Reportes generados correctamente.")

    def open_file(self, file_type):
        try:
            if file_type == "excel":
                file_path = os.path.join(
                    self.output_dir.get(), "reporte_completo.xlsx")
            elif file_type == "markdown":
                file_path = os.path.join(
                    self.output_dir.get(), "reporte_completo.md")
            else:
                file_path = os.path.join(
                    self.output_dir.get(), "reporte_completo.pdf")
            if os.path.exists(file_path):
                if sys.platform == "win32":
                    os.startfile(file_path)
                elif sys.platform == "darwin":
                    os.system(f"open '{file_path}'")
                else:
                    os.system(f"xdg-open '{file_path}'")
            else:
                messagebox.showerror(
                    "Error", f"El archivo {file_path} no existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")


if __name__ == "__main__":
    app = GithubReportApp()
    app.mainloop()
