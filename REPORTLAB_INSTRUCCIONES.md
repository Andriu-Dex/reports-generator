# Instrucciones para generar PDFs con ReportLab

ReportLab es una biblioteca de Python que permite generar documentos PDF de alta calidad de manera programática.

## Instalación

Para instalar ReportLab, simplemente ejecuta:

```
pip install reportlab markdown2
```

## Ventajas de ReportLab

1. **Fácil de instalar**: No requiere dependencias externas complejas.
2. **Multiplataforma**: Funciona en Windows, macOS y Linux sin necesidad de configuraciones especiales.
3. **Control preciso**: Permite un control detallado sobre el diseño y formato del PDF.
4. **Rendimiento**: Generalmente más rápido que otras soluciones basadas en navegadores.

## Características implementadas

El generador de PDF ahora incluye las siguientes características avanzadas:

1. **Portada profesional**: Con título, subtítulo y fecha de generación formateados profesionalmente.
2. **Índice de contenido**: Listado organizado de las secciones del reporte.
3. **Tablas de resumen mejoradas**: Con formato de colores que distingue entre issues abiertos y cerrados.
4. **Encabezados y pies de página**: Incluye nombre del repositorio, fecha y número de página en todas las páginas.
5. **Estilos visuales mejorados**: Uso de la paleta de colores de GitHub para crear un diseño coherente.
6. **Secciones organizadas**: Agrupación de issues y PRs por estado (abiertos/cerrados).
7. **Formato optimizado**: Mejor espaciado, tipografía y diseño para facilitar la lectura.

## Personalización

El sistema está configurado para generar PDFs con un estilo visual atractivo, pero ReportLab ofrece muchas opciones de personalización adicionales:

- Fuentes personalizadas
- Imágenes y gráficos
- Tablas complejas
- Marcas de agua
- Estilos avanzados

Para modificar el aspecto visual, puedes editar la función `generar_pdf_desde_markdown()` en el archivo `reporte_issues.py`. Los principales elementos que puedes personalizar son:

- Colores (variable `GITHUB_BLUE`, `GITHUB_GREEN`, etc.)
- Estilos de texto (objetos `ParagraphStyle`)
- Diseño de tablas (método `setStyle` con `TableStyle`)
- Márgenes y tamaño de página (parámetros de `SimpleDocTemplate`)

Para más información, consulta la [documentación oficial de ReportLab](https://docs.reportlab.com/).

## Solución de problemas

Si encuentras problemas al generar PDFs:

1. Asegúrate de tener las versiones más recientes de ReportLab y markdown2:

   ```
   pip install --upgrade reportlab markdown2
   ```

2. Verifica que la variable `ENABLE_PDF` esté configurada como `true` en tu archivo `.env`.

3. Si tienes problemas con caracteres especiales, asegúrate de que todos los archivos estén en codificación UTF-8.

4. Para solucionar problemas de formato específicos, revisa el archivo markdown generado (`reporte_completo.md`) y verifica que su estructura sea correcta.

5. Si necesitas más espacio para texto largo, puedes ajustar los márgenes y el tamaño de fuente en la configuración del documento.
