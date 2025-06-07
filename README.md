# Generador de Reportes de GitHub

Este script genera reportes detallados de issues y pull requests de un repositorio de GitHub.

## Características

- Extrae información de issues y pull requests
- Vincula commits relacionados
- Incluye comentarios de cada issue
- Genera reportes en formato Excel, Markdown y PDF (opcional)

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

3. Para generar PDFs (opcional), instala WeasyPrint siguiendo las instrucciones en:
   https://doc.courtbouillon.org/weasyprint/stable/first_steps.html

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto con la siguiente información:

   ```
   GITHUB_TOKEN=tu_token_de_github
   REPO=usuario/repositorio
   ```

   Puedes obtener un token de GitHub en: https://github.com/settings/tokens

## Uso

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
- Si encuentras problemas con la generación de PDFs, revisa las instrucciones de instalación de WeasyPrint para tu sistema operativo.
