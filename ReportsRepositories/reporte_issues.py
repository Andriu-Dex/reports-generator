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
    import markdown2
    from weasyprint import HTML
    PDF_DISPONIBLE = True
except ImportError:
    print("Nota: Algunas dependencias para generar PDF no están disponibles.")
    print("Para instalar todas las dependencias en Windows, siga las instrucciones en:")
    print("https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows")

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
    df = pd.DataFrame(filas)
    df.to_excel("reporte_completo.xlsx", index=False)

def generar_markdown(filas):
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
    with open("reporte_completo.md", "w", encoding="utf-8") as f:
        f.write(markdown)

def generar_pdf_desde_markdown():
    if not PDF_DISPONIBLE:
        print("No se puede generar PDF: Faltan dependencias necesarias.")
        return
        
    with open("reporte_completo.md", "r", encoding="utf-8") as f:
        html = markdown2.markdown(f.read())
    HTML(string=html).write_pdf("reporte_completo.pdf")

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
    generar_pdf_desde_markdown()

    print("✅ Archivos generados:")
    print("- reporte_completo.xlsx")
    print("- reporte_completo.md")
    print("- reporte_completo.pdf")
