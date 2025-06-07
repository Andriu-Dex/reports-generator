import requests
import pandas as pd
import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
# Importar GitHubAnalytics para estadísticas
from analytics import GitHubAnalytics

# Cargar variables de entorno
# Primero intenta cargar desde el directorio actual
env_loaded = load_dotenv()

# Si no encuentra el archivo .env en el directorio actual, intenta
# buscarlo en el directorio raíz
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
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib import colors
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
        return "\n".join(
            [f"- {c['user']['login']}: {c['body']}" for c in comentarios])
    return ""


def generar_excel(filas):
    # Crear directorio de reportes si no existe
    carpeta_reportes = "reportes"
    os.makedirs(carpeta_reportes, exist_ok=True)

    df = pd.DataFrame(filas)
    df.to_excel(
        os.path.join(
            carpeta_reportes,
            "reporte_completo.xlsx"),
        index=False)


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


def generar_pdf_desde_markdown(filas=None):
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

        # Extraer nombre de repositorio y organización
        repo_parts = REPO.split('/')
        org_name = repo_parts[0] if len(repo_parts) > 0 else ""
        repo_name = repo_parts[1] if len(repo_parts) > 1 else ""

        # Crear función para encabezado y pie de página
        def add_page_number(canvas, doc):
            # Guardar estado
            canvas.saveState()

            # Dibujar encabezado
            canvas.setFillColor(colors.darkblue)
            canvas.setFont('Helvetica-Bold', 8)
            canvas.drawString(
                doc.leftMargin,
                doc.height + doc.topMargin - 10,
                f"Reporte GitHub: {REPO}")

            # Dibujar una línea separadora
            canvas.setStrokeColor(colors.darkblue)
            canvas.line(
                doc.leftMargin,
                doc.height + doc.topMargin - 15,
                doc.width + doc.leftMargin,
                doc.height + doc.topMargin - 15)

            # Dibujar fecha en esquina superior derecha
            current_date = pd.Timestamp.now().strftime('%d-%m-%Y')
            date_width = canvas.stringWidth(current_date, 'Helvetica', 8)
            canvas.setFont('Helvetica', 8)
            canvas.drawString(doc.width + doc.leftMargin - date_width,
                              doc.height + doc.topMargin - 10, current_date)

            # Dibujar pie de página con número de página
            page_num = canvas.getPageNumber()
            canvas.setFont('Helvetica', 8)
            canvas.drawString(
                doc.leftMargin,
                doc.bottomMargin - 20,
                f"Página {page_num}")

            # Línea separadora en pie de página
            canvas.line(doc.leftMargin, doc.bottomMargin - 15,
                        doc.width + doc.leftMargin, doc.bottomMargin - 15)

            # Restaurar estado
            canvas.restoreState()

        # Crear un documento PDF
        pdf_path = os.path.join(carpeta_reportes, "reporte_completo.pdf")
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=60,
            bottomMargin=50
        )

        # Definir paleta de colores personalizada
        GITHUB_BLUE = colors.Color(0.125, 0.416, 0.702)   # Azul de GitHub
        GITHUB_GREEN = colors.Color(0.157, 0.675, 0.235)  # Verde de GitHub
        GITHUB_RED = colors.Color(0.835, 0.243, 0.309)    # Rojo de GitHub
        GITHUB_PURPLE = colors.Color(0.584, 0.345, 0.698)  # Púrpura de GitHub
        GITHUB_GRAY = colors.Color(0.6, 0.6, 0.6)         # Gris de GitHub

        # Definir estilos personalizados
        styles = getSampleStyleSheet()

        # Estilo para el título principal
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=GITHUB_BLUE,
            spaceAfter=16,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Estilo para el subtítulo en la portada
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=GITHUB_BLUE,
            spaceBefore=10,
            spaceAfter=16,
            alignment=TA_CENTER,
        ))

        # Estilo para subtítulos
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=GITHUB_BLUE,
            spaceBefore=14,
            spaceAfter=8,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=6,
            borderRadius=6,
            leading=20
        ))

        # Estilo para sub-subtítulos
        styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=GITHUB_PURPLE,
            spaceBefore=10,
            spaceAfter=6,
            leading=16
        ))

        # Estilo para el texto normal
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=4,
            spaceAfter=6,
            leading=14
        ))

        # Estilo para fecha
        styles.add(ParagraphStyle(
            name='DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=GITHUB_GRAY,
            alignment=TA_CENTER
        ))

        # Estilo para issue abierto
        styles.add(ParagraphStyle(
            name='IssueOpen',
            parent=styles['CustomHeading2'],
            backColor=colors.Color(0.95, 0.95, 1.0),  # Lavender claro
            borderColor=GITHUB_PURPLE,
        ))

        # Estilo para PR abierto
        styles.add(ParagraphStyle(
            name='PROpen',
            parent=styles['CustomHeading2'],
            backColor=colors.Color(0.9, 1.0, 0.9),  # Verde claro
            borderColor=GITHUB_GREEN,
        ))

        # Estilo para issue/PR cerrado
        styles.add(ParagraphStyle(
            name='Closed',
            parent=styles['CustomHeading2'],
            backColor=colors.Color(0.95, 0.95, 0.95),  # Gris claro
            borderColor=GITHUB_GRAY,
        ))

        # Elementos que formarán el PDF
        elements = []

        # === PORTADA ===

        # Añadir un espacio al principio
        elements.append(Spacer(1, 1.5 * inch))

        # Logo de GitHub (simulado con texto estilizado)
        elements.append(Paragraph(
            '<font size="38" color="#333333"><b>GitHub</b></font>',
            styles['Title']
        ))
        elements.append(Spacer(1, 0.5 * inch))

        # Título del reporte
        elements.append(Paragraph(
            f"Reporte de Issues y Pull Requests",
            styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.25 * inch))

        # Subtítulo con nombre del repositorio
        repo_display = f"{org_name}/<b>{repo_name}</b>"
        elements.append(Paragraph(
            repo_display,
            styles['CoverSubtitle']
        ))

        # Añadir fecha de generación
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(
            Paragraph(
                f"Generado el {
                    pd.Timestamp.now().strftime('%d de %B de %Y, %H:%M')}",
                styles['DateStyle']))

        elements.append(Spacer(1, 1.5 * inch))

        # Extraer texto del HTML
        import re
        text = re.sub(r'<[^>]*>', '', html)

        # Procesar el contenido
        lines = text.split('\n')
        current_section = None
        issue_count = {
            'issue_open': 0,
            'issue_closed': 0,
            'pr_open': 0,
            'pr_closed': 0}

        # Primera pasada: contar tipos de issues para el resumen
        for line in lines:
            if line.strip() and "Issue #" in line and "state: open" in line.lower():
                issue_count['issue_open'] += 1
            elif line.strip() and "Issue #" in line and "state: closed" in line.lower():
                issue_count['issue_closed'] += 1
            elif line.strip() and "Pull Request #" in line and "state: open" in line.lower():
                issue_count['pr_open'] += 1
            elif line.strip() and "Pull Request #" in line and "state: closed" in line.lower():
                issue_count['pr_closed'] += 1
          # === TABLA RESUMEN ===

        # Título de la sección de resumen
        elements.append(
            Paragraph(
                "Resumen del Repositorio",
                styles['CustomHeading3']))
        elements.append(Spacer(1, 0.2 * inch))

        # Generar estadísticas avanzadas con analytics si hay datos disponibles
        stats_avanzadas = {}
        if filas:
            try:
                # Inicializar GitHubAnalytics con los datos
                analytics = GitHubAnalytics(filas)
                # Obtener estadísticas detalladas
                stats_avanzadas = analytics.obtener_estadisticas_resumen()
                print(
                    f"Estadísticas generadas con GitHubAnalytics: {
                        len(stats_avanzadas)} métricas")
            except Exception as e:
                print(f"Error al generar estadísticas avanzadas: {e}")

        # Si tenemos estadísticas avanzadas, usarlas
        if stats_avanzadas:
            # Usar los valores de GitHubAnalytics
            issue_count['issue_open'] = stats_avanzadas.get(
                'issues_abiertos', issue_count['issue_open'])
            issue_count['issue_closed'] = stats_avanzadas.get(
                'issues_cerrados', issue_count['issue_closed'])
            issue_count['pr_open'] = stats_avanzadas.get(
                'prs_abiertos', issue_count['pr_open'])
            issue_count['pr_closed'] = stats_avanzadas.get(
                'prs_cerrados', issue_count['pr_closed'])

        # Tabla de resumen mejorada
        table_data = [
            ['', 'Abiertos', 'Cerrados', 'Total'],
            ['Issues', issue_count['issue_open'], issue_count['issue_closed'],
             issue_count['issue_open'] + issue_count['issue_closed']],
            ['Pull Requests', issue_count['pr_open'], issue_count['pr_closed'],
             issue_count['pr_open'] + issue_count['pr_closed']],
            ['Total',
             issue_count['issue_open'] + issue_count['pr_open'],
             issue_count['issue_closed'] + issue_count['pr_closed'],
             sum(issue_count.values())]
        ]

        # Crear tabla de resumen con mejor formato
        table = Table(table_data, colWidths=[120, 80, 80, 80])
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), GITHUB_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),

            # Primera columna (tipos)
            ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.95, 0.95, 0.95)),
            ('TEXTCOLOR', (0, 1), (0, -1), GITHUB_BLUE),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),

            # Contenido - abiertos (verde)
            ('BACKGROUND', (1, 1), (1, -2), colors.Color(0.9, 1.0, 0.9)),
            ('TEXTCOLOR', (1, 1), (1, -1), GITHUB_GREEN),

            # Contenido - cerrados (gris)
            ('BACKGROUND', (2, 1), (2, -2), colors.Color(0.95, 0.95, 0.95)),
            ('TEXTCOLOR', (2, 1), (2, -1), GITHUB_GRAY),

            # Totales
            ('BACKGROUND', (3, 1), (3, -2), colors.Color(0.95, 0.95, 1.0)),
            ('BACKGROUND', (0, -1), (-1, -1), GITHUB_BLUE),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, GITHUB_BLUE),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # Añadir estadísticas avanzadas si están disponibles
        if stats_avanzadas and len(stats_avanzadas) > 4:
            elements.append(
                Paragraph(
                    "Estadísticas Detalladas",
                    styles['CustomHeading3']))
            elements.append(Spacer(1, 0.15 * inch))

            # Crear una tabla para las estadísticas avanzadas
            advanced_stats_data = [
                [
                    'Métrica', 'Valor'], [
                    'Tiempo promedio de resolución', f"{
                        stats_avanzadas.get(
                            'tiempo_promedio_resolucion', 0)} días"], [
                        'Tiempo mediano de resolución', f"{
                            stats_avanzadas.get(
                                'tiempo_mediano_resolucion', 0)} días"], [
                                    'Contribuidores únicos', f"{
                                        stats_avanzadas.get(
                                            'contribuidores_unicos', 0)}"], [
                                                'Período de análisis', f"{
                                                    stats_avanzadas.get(
                                                        'fecha_min', 'N/A')} a {
                                                            stats_avanzadas.get(
                                                                'fecha_max', 'N/A')}"]]

            # Crear tabla de estadísticas avanzadas
            advanced_stats_table = Table(
                advanced_stats_data, colWidths=[200, 160])
            advanced_stats_table.setStyle(TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), GITHUB_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Primera columna (métricas)
                ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.95, 0.95, 0.95)),
                ('TEXTCOLOR', (0, 1), (0, -1), GITHUB_BLUE),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),

                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(advanced_stats_table)
            elements.append(Spacer(1, 0.2 * inch))

        # Información adicional
        if sum(issue_count.values()) > 0:
            # Cálculo de porcentajes
            porcentaje_abiertos = (
                issue_count['issue_open'] + issue_count['pr_open']) / sum(issue_count.values()) * 100
            porcentaje_cerrados = (
                issue_count['issue_closed'] + issue_count['pr_closed']) / sum(issue_count.values()) * 100

            elements.append(
                Paragraph(
                    f"<b>Estado del repositorio:</b> {
                        porcentaje_abiertos:.1f}% abiertos, {
                        porcentaje_cerrados:.1f}% cerrados",
                    styles['CustomNormal']))

        # Añadir página nueva
        elements.append(PageBreak())

        # === ÍNDICE DE CONTENIDO ===
        elements.append(
            Paragraph(
                "Índice de Contenido",
                styles['CustomTitle']))
        elements.append(Spacer(1, 0.25 * inch))

        # Crear un índice simple
        if issue_count['issue_open'] > 0:
            elements.append(
                Paragraph(
                    "1. Issues Abiertos",
                    styles['CustomHeading3']))
        if issue_count['issue_closed'] > 0:
            elements.append(
                Paragraph(
                    "2. Issues Cerrados",
                    styles['CustomHeading3']))
        if issue_count['pr_open'] > 0:
            elements.append(
                Paragraph(
                    "3. Pull Requests Abiertos",
                    styles['CustomHeading3']))
        if issue_count['pr_closed'] > 0:
            elements.append(
                Paragraph(
                    "4. Pull Requests Cerrados",
                    styles['CustomHeading3']))

        elements.append(PageBreak())

        # === CONTENIDO DETALLADO ===

        # Segunda pasada: procesar el contenido
        in_issue_block = False
        current_issue = {}
        section_counter = 0
        last_section = None

        for line in lines:
            if line.strip():
                # Detectar inicio de un nuevo issue/PR
                if line.startswith('# '):
                    elements.append(Paragraph(line[2:], styles['CustomTitle']))
                    elements.append(Spacer(1, 0.25 * inch))

                elif line.startswith('## '):
                    # Determinar tipo de sección
                    current_section = None
                    if "Issue #" in line and "state: open" in line.lower():
                        current_section = "issue_open"
                    elif "Issue #" in line and "state: closed" in line.lower():
                        current_section = "issue_closed"
                    elif "Pull Request #" in line and "state: open" in line.lower():
                        current_section = "pr_open"
                    elif "Pull Request #" in line and "state: closed" in line.lower():
                        current_section = "pr_closed"

                    # Si cambiamos de tipo de sección, agregar encabezado de
                    # sección
                    if current_section != last_section:
                        section_counter += 1
                        if current_section == "issue_open":
                            elements.append(
                                Paragraph(
                                    f"{section_counter}. Issues Abiertos",
                                    styles['CustomTitle']))
                        elif current_section == "issue_closed":
                            elements.append(
                                Paragraph(
                                    f"{section_counter}. Issues Cerrados",
                                    styles['CustomTitle']))
                        elif current_section == "pr_open":
                            elements.append(
                                Paragraph(
                                    f"{section_counter}. Pull Requests Abiertos",
                                    styles['CustomTitle']))
                        elif current_section == "pr_closed":
                            elements.append(
                                Paragraph(
                                    f"{section_counter}. Pull Requests Cerrados",
                                    styles['CustomTitle']))

                        elements.append(Spacer(1, 0.5 * inch))
                        last_section = current_section

                    if in_issue_block:
                        # Añadir separador entre issues
                        elements.append(Spacer(1, 0.25 * inch))
                        elements.append(PageBreak())

                    in_issue_block = True

                    # Aplicar estilo según tipo
                    if "Issue #" in line and "state: open" in line.lower():
                        style_to_use = 'IssueOpen'
                    elif "Pull Request #" in line and "state: open" in line.lower():
                        style_to_use = 'PROpen'
                    else:  # Cerrado
                        style_to_use = 'Closed'

                    # Extraer número para formato
                    numero_match = re.search(r'#(\d+)', line)
                    numero = numero_match.group(1) if numero_match else ""

                    # Mejorar formato del título
                    titulo_issue = line[3:]
                    elementos_titulo = titulo_issue.split(" - ", 1)
                    if len(elementos_titulo) > 1:
                        identificador = elementos_titulo[0]
                        titulo_real = elementos_titulo[1]
                        titulo_formateado = f"{identificador}<br/><font size='14'>{titulo_real}</font>"
                    else:
                        titulo_formateado = titulo_issue

                    p = Paragraph(titulo_formateado, styles[style_to_use])
                    elements.append(p)

                elif line.startswith('### '):
                    elements.append(Spacer(1, 0.1 * inch))
                    elements.append(
                        Paragraph(line[4:], styles['CustomHeading3']))

                elif line.startswith('**'):
                    # Mejorar formato de metadatos
                    metadata_text = line

                    # Colorear según estado
                    if "state: open" in metadata_text.lower():
                        metadata_text = metadata_text.replace(
                            "state: open",
                            "<font color='#28a745'><b>state: OPEN</b></font>"
                        )
                    elif "state: closed" in metadata_text.lower():
                        metadata_text = metadata_text.replace(
                            "state: closed",
                            "<font color='#cb2431'><b>state: CLOSED</b></font>"
                        )

                    # Estilo para metadatos
                    metadata_style = ParagraphStyle(
                        name='Metadata',
                        parent=styles['CustomNormal'],
                        backColor=colors.Color(
                            0.97, 0.97, 0.97),  # Gris muy claro
                        borderPadding=6,
                        borderWidth=0.5,
                        borderColor=colors.lightgrey,
                        borderRadius=4
                    )
                    elements.append(Paragraph(metadata_text, metadata_style))

                else:
                    # Texto normal
                    # Saltar líneas vacías o separadores
                    if line.strip() == '---':
                        elements.append(Spacer(1, 0.1 * inch))
                    else:
                        # Sanitizar texto con caracteres especiales
                        line = line.replace("✅", "(Correcto)")
                        line = line.replace("❌", "(Error)")
                        line = line.replace("⚠️", "(Advertencia)")

                        # Añadir formato para enlaces si existen - con mejor
                        # manejo de caracteres especiales
                        if "http://" in line or "https://" in line:
                            try:
                                # Patrón de URL más seguro
                                pattern = r'(https?://[^\s"\'<>]+)'
                                # Reemplazar URLs sin caracteres problemáticos
                                line = re.sub(
                                    pattern, lambda m: f'<link href="{
                                        m.group(1).strip()}">{
                                        m.group(1).strip()}</link>', line)
                            except BaseException:
                                # Si hay error en el procesamiento de enlaces,
                                # mostrar texto plano
                                pass

                        elements.append(
                            Paragraph(
                                line, styles['CustomNormal']))
                        elements.append(Spacer(1, 0.05 * inch))

        # Construir el PDF con funciones de encabezado y pie de página
        doc.build(
            elements,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number)

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
        generar_pdf_desde_markdown(filas)
        print("✅ Archivos generados:")
        print("- reportes/reporte_completo.xlsx")
        print("- reportes/reporte_completo.md")
        print("- reportes/reporte_completo.pdf")
    else:
        print("✅ Archivos generados:")
        print("- reportes/reporte_completo.xlsx")
        print("- reportes/reporte_completo.md")
        print("⚠️ El archivo PDF no se generó debido a que falta instalar ReportLab.")
