# Generador de Reportes de GitHub

Este script genera reportes detallados de issues y pull requests de un repositorio de GitHub.

## Características

- Extrae información de issues y pull requests
- Vincula commits relacionados
- Incluye comentarios de cada issue
- Genera reportes en formato Excel, Markdown y PDF (opcional)
- Interfaz gráfica para facilitar su uso

## Requisitos

- Python 3.6 o superior
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clona este repositorio:

   ```
   git clone <url-del-repositorio>
   cd Reportes_Github
   ```

2. Instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

3. Para generar PDFs (opcional), instala ReportLab:
   ```
   pip install reportlab markdown2
   ```

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto con la siguiente información:

   ```
   GITHUB_TOKEN=tu_token_de_github
   REPO=usuario/repositorio
   ```

   Puedes obtener un token de GitHub en: https://github.com/settings/tokens

## Uso

### Interfaz Gráfica

Para iniciar la aplicación con interfaz gráfica, ejecute:

```
# En Windows - Con batch
iniciar_app.bat

# En Windows - Con PowerShell
.\iniciar_app.ps1

# Manualmente
python ReportsRepositories\app_gui.py
```

### Línea de Comandos

```
cd ReportsRepositories
python reporte_issues.py
```

El script generará tres archivos en la carpeta `reportes`:

- `reporte_completo.xlsx`: Reporte en formato Excel
- `reporte_completo.md`: Reporte en formato Markdown
- `reporte_completo.pdf`: Reporte en formato PDF (si WeasyPrint está instalado)

## Notas

- Asegúrate de que tu token de GitHub tenga los permisos necesarios para acceder al repositorio.
- Si encuentras problemas con la generación de PDFs, revisa las instrucciones de instalación de ReportLab en el archivo `REPORTLAB_INSTRUCCIONES.md`.
