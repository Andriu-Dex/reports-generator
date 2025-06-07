import requests
import pandas as pd
import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
# Primero intenta cargar desde el directorio actual
env_loaded = load_dotenv()

# Si no encuentra el archivo .env en el directorio actual, intenta buscarlo en el directorio raíz
if not env_loaded:
    root_dir = Path(__file__).resolve().parent.parent
    load_dotenv(root_dir / ".env")

# === CONFIGURACIÓN ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")  # Ejemplo: openai/chatgpt

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
BASE_URL = f"https://github.com/{REPO}"

# Importaciones opcionales para generación de PDF
PDF_DISPONIBLE = False
try:
    # Solo verificamos si las dependencias están disponibles al inicio
    import markdown2
    import reportlab
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    PDF_DISPONIBLE = os.getenv("ENABLE_PDF", "").lower() == "true"
except ImportError:
    print("Nota: Algunas dependencias para generar PDF no están disponibles.")
    print("Para instalar las dependencias necesarias ejecute:")
    print("pip install reportlab markdown2")

def obtener_issues_y_prs():
    resultados = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        if not data:
            break
        resultados.extend(data)
        page += 1
    return resultados

def obtener_commits():
    commits = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO}/commits?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        if not data or "message" in data:
            break
        commits.extend(data)
        page += 1
    return commits

def vincular_commits(issue_number, commits):
    vinculados = []
    autores = set()
    patron = re.compile(rf"#({issue_number})\b")

    for commit in commits:
        mensaje = commit["commit"]["message"]
        if patron.search(mensaje):
            vinculados.append(mensaje.splitlines()[0])
            autor = commit["commit"]["author"]["name"]
            autores.add(autor)

    return "; ".join(vinculados), ", ".join(autores)

def obtener_comentarios(numero):
    url = f"https://api.github.com/repos/{REPO}/issues/{numero}/comments"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        comentarios = r.json()
        return "\n".join([f"- {c['user']['login']}: {c['body']}" for c in comentarios])
    return ""

def generar_excel(filas):
    # Crear directorio de reportes si no existe
    carpeta_reportes = "reportes"
    os.makedirs(carpeta_reportes, exist_ok=True)
    
    df = pd.DataFrame(filas)
    df.to_excel(os.path.join(carpeta_reportes, "reporte_completo.xlsx"), index=False)

def generar_markdown(filas):
    # Crear directorio de reportes si no existe
    carpeta_reportes = "reportes"
    os.makedirs(carpeta_reportes, exist_ok=True)
    
    markdown = "# Reporte de Issues y Pull Requests\n\n"
    for item in filas:
        markdown += f"""
## [{item['Tipo']} #{item['ID']}]({item['URL']}) - {item['Título']}

**Estado:** {item['Estado']}  
**Asignado a:** {item['Asignado a']}  
**Creado:** {item['Creado']}  
**Cerrado:** {item['Cerrado']}  

### Descripción
{item['Descripción']}

### Commits Vinculados
{item['Commits Vinculados']}

### Autores de Commits
{item['Autores Commits']}

### Comentarios
{item['Comentarios']}

---

"""
    with open(os.path.join(carpeta_reportes, "reporte_completo.md"), "w", encoding="utf-8") as f:
        f.write(markdown)

def generar_pdf_desde_markdown():
    if not PDF_DISPONIBLE:
        print("No se puede generar PDF: Faltan dependencias necesarias.")
        print("Consulta el archivo REPORTLAB_INSTRUCCIONES.md para más información.")
        return
        
    try:
        # Crear directorio de reportes si no existe
        carpeta_reportes = "reportes"
        os.makedirs(carpeta_reportes, exist_ok=True)
        
        # Leer el archivo markdown
        with open(os.path.join(carpeta_reportes, "reporte_completo.md"), "r", encoding="utf-8") as f:
            md_text = f.read()
            
        # Convertir markdown a HTML
        html = markdown2.markdown(md_text)
        
        # Crear un documento PDF
        pdf_path = os.path.join(carpeta_reportes, "reporte_completo.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        
        # Estilos para el PDF
        styles = getSampleStyleSheet()
        story = []
        
        # Extraer texto del HTML (esto es simplificado, idealmente se procesaría mejor el HTML)
        import re
        # Eliminar etiquetas HTML básicas
        text = re.sub(r'<[^>]*>', '', html)
        
        # Dividir en líneas para procesar
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                # Distinguir entre títulos y contenido regular
                if line.startswith('# '):
                    # Título principal
                    story.append(Paragraph(line[2:], styles['Title']))
                elif line.startswith('## '):
                    # Subtítulo
                    story.append(Paragraph(line[3:], styles['Heading2']))
                elif line.startswith('### '):
                    # Sub-subtítulo
                    story.append(Paragraph(line[4:], styles['Heading3']))
                else:
                    # Contenido regular
                    story.append(Paragraph(line, styles['Normal']))
                    
        # Construir el PDF
        doc.build(story)
        return True
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        print("Consulta el archivo REPORTLAB_INSTRUCCIONES.md para más información.")
        return False

def procesar_reporte(issues, commits):
    filas = []

    for issue in issues:
        tipo = "Pull Request" if "pull_request" in issue else "Issue"
        numero = issue["number"]
        titulo = issue["title"]
        descripcion = issue.get("body", "").strip()
        estado = issue["state"]
        creado = issue["created_at"]
        cerrado = issue.get("closed_at", "")
        asignado = issue["assignee"]["login"] if issue["assignee"] else "No asignado"
        url = issue["html_url"]
        comentarios = obtener_comentarios(numero)
        commits_texto, autores = vincular_commits(numero, commits)

        filas.append({
            "ID": numero,
            "Tipo": tipo,
            "Título": titulo,
            "Descripción": descripcion,
            "Estado": estado,
            "Asignado a": asignado,
            "Creado": creado,
            "Cerrado": cerrado,
            "Comentarios": comentarios or "Sin comentarios",
            "Commits Vinculados": commits_texto or "Ninguno",
            "Autores Commits": autores or "Ninguno",
            "URL": url
        })

    return filas

if __name__ == "__main__":
    issues_y_prs = obtener_issues_y_prs()
    commits = obtener_commits()
    filas = procesar_reporte(issues_y_prs, commits)

    generar_excel(filas)
    generar_markdown(filas)
    
    if PDF_DISPONIBLE:
        generar_pdf_desde_markdown()
        print("✅ Archivos generados:")
        print("- reportes/reporte_completo.xlsx")
        print("- reportes/reporte_completo.md")
        print("- reportes/reporte_completo.pdf")
    else:
        print("✅ Archivos generados:")
        print("- reportes/reporte_completo.xlsx")
        print("- reportes/reporte_completo.md")
        print("⚠️ El archivo PDF no se generó debido a que falta instalar WeasyPrint.")
