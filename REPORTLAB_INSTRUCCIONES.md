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

## Personalización

El sistema está configurado para generar PDFs básicos, pero ReportLab ofrece muchas opciones de personalización:

- Fuentes personalizadas
- Imágenes y gráficos
- Tablas complejas
- Encabezados y pies de página
- Marcas de agua
- Estilos avanzados

Para más información, consulta la [documentación oficial de ReportLab](https://docs.reportlab.com/).

## Solución de problemas

Si encuentras problemas al generar PDFs:

1. Asegúrate de tener las versiones más recientes de ReportLab y markdown2:
   ```
   pip install --upgrade reportlab markdown2
   ```

2. Verifica que la variable `ENABLE_PDF` esté configurada como `true` en tu archivo `.env`.

3. Si tienes problemas con caracteres especiales, asegúrate de que todos los archivos estén en codificación UTF-8.
