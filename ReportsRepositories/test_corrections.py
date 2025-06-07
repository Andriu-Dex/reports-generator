#!/usr/bin/env python3
"""
Script de prueba para verificar que las correcciones de analytics funcionan correctamente
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from analytics import GitHubAnalytics

def create_test_data():
    """Crear datos de prueba simulados"""
    test_data = [
        {
            'Tipo': 'Issue',
            'Estado': 'open',
            'Titulo': 'Bug en el sistema de autenticación',
            'Descripcion': 'Error al hacer login con credenciales válidas',
            'Autor': 'usuario1',
            'Fecha_Creacion': '2024-01-15T10:30:00Z',
            'Fecha_Cerrado': None,
            'Etiquetas': 'bug, priority-high'
        },
        {
            'Tipo': 'Issue',
            'Estado': 'closed',
            'Titulo': 'Feature request: Dashboard analytics',
            'Descripcion': 'Necesitamos un dashboard para visualizar métricas',
            'Autor': 'usuario2',
            'Fecha_Creacion': '2024-01-10T09:00:00Z',
            'Fecha_Cerrado': '2024-01-20T16:45:00Z',
            'Etiquetas': 'feature, enhancement'
        },
        {
            'Tipo': 'Pull Request',
            'Estado': 'open',
            'Titulo': 'Fix authentication bug',
            'Descripcion': 'Esta PR soluciona el bug de autenticación reportado',
            'Autor': 'usuario1',
            'Fecha_Creacion': '2024-01-16T14:20:00Z',
            'Fecha_Cerrado': None,
            'Etiquetas': 'bug-fix'
        },
        {
            'Tipo': 'Pull Request',
            'Estado': 'closed',
            'Titulo': 'Add new dashboard feature',
            'Descripcion': 'Implementación del dashboard solicitado',
            'Autor': 'usuario3',
            'Fecha_Creacion': '2024-01-12T11:15:00Z',
            'Fecha_Cerrado': '2024-01-25T13:30:00Z',
            'Etiquetas': 'feature, ui'
        },
        {
            'Tipo': 'Issue',
            'Estado': 'closed',
            'Titulo': 'Documentation update needed',
            'Descripcion': 'La documentación está desactualizada',
            'Autor': 'usuario2',
            'Fecha_Creacion': '2024-01-05T08:45:00Z',
            'Fecha_Cerrado': '2024-01-08T17:20:00Z',
            'Etiquetas': 'documentation'
        }
    ]
    return test_data

def test_analytics_functionality():
    """Probar las funcionalidades de analytics"""
    print("🧪 Iniciando pruebas de Analytics...")
    
    # Crear datos de prueba
    test_data = create_test_data()
    print(f"✅ Datos de prueba creados: {len(test_data)} elementos")
    
    # Inicializar GitHubAnalytics
    try:
        analytics = GitHubAnalytics(test_data)
        print("✅ GitHubAnalytics inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar GitHubAnalytics: {e}")
        return False
    
    # Probar preparación de datos
    try:
        df = analytics.df
        print(f"✅ DataFrame preparado: {len(df)} filas, {len(df.columns)} columnas")
        print(f"   Columnas: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error al preparar datos: {e}")
        return False
    
    # Probar filtros
    try:
        filters = {
            'state': 'open',
            'item_type': 'Issue'
        }
        filtered_data = analytics.filter_data(test_data, filters)
        print(f"✅ Filtros funcionando: {len(filtered_data)} elementos filtrados")
    except Exception as e:
        print(f"❌ Error en filtros: {e}")
        return False
    
    # Probar generación de gráficos
    try:
        # Gráfico de tendencias
        fig_tendencias = analytics.grafico_tendencias_mensual()
        print("✅ Gráfico de tendencias generado")
        
        # Gráfico de contribuidores
        fig_contrib = analytics.grafico_contribuidores_activos()
        print("✅ Gráfico de contribuidores generado")
        
        # Gráfico de tiempo de resolución
        fig_tiempo = analytics.grafico_tiempo_resolucion()
        print("✅ Gráfico de tiempo de resolución generado")
        
        # Gráfico de etiquetas
        fig_etiquetas = analytics.grafico_etiquetas_populares()
        print("✅ Gráfico de etiquetas generado")
        
    except Exception as e:
        print(f"❌ Error al generar gráficos: {e}")
        return False
    
    # Probar generación de dashboard
    try:
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        dashboard_path = analytics.generate_dashboard(test_data, output_dir, "test/repo")
        
        if dashboard_path and os.path.exists(dashboard_path):
            print(f"✅ Dashboard generado correctamente: {dashboard_path}")
        else:
            print("❌ Error: Dashboard no se generó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error al generar dashboard: {e}")
        return False
    
    # Probar exportación de datos filtrados
    try:
        export_path = analytics.export_filtered_data(filtered_data, output_dir)
        if export_path and os.path.exists(export_path):
            print(f"✅ Datos filtrados exportados: {export_path}")
        else:
            print("❌ Error: Exportación falló")
            return False
    except Exception as e:
        print(f"❌ Error al exportar datos: {e}")
        return False
    
    print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    return True

def test_filter_functionality():
    """Probar específicamente la funcionalidad de filtros"""
    print("\n🔍 Probando funcionalidades de filtros...")
    
    test_data = create_test_data()
    analytics = GitHubAnalytics(test_data)
    
    # Prueba 1: Filtro por estado
    filters = {'state': 'open'}
    filtered = analytics.filter_data(test_data, filters)
    open_count = len([d for d in test_data if d['Estado'] == 'open'])
    print(f"✅ Filtro por estado 'open': {len(filtered)}/{open_count} elementos")
    
    # Prueba 2: Filtro por tipo
    filters = {'item_type': 'Issue'}
    filtered = analytics.filter_data(test_data, filters)
    issue_count = len([d for d in test_data if d['Tipo'] == 'Issue'])
    print(f"✅ Filtro por tipo 'Issue': {len(filtered)}/{issue_count} elementos")
    
    # Prueba 3: Filtro por autor
    filters = {'author': 'usuario1'}
    filtered = analytics.filter_data(test_data, filters)
    user1_count = len([d for d in test_data if d['Autor'] == 'usuario1'])
    print(f"✅ Filtro por autor 'usuario1': {len(filtered)}/{user1_count} elementos")
    
    # Prueba 4: Filtro por búsqueda de texto
    filters = {'search_text': 'bug'}
    filtered = analytics.filter_data(test_data, filters)
    print(f"✅ Filtro por texto 'bug': {len(filtered)} elementos encontrados")
    
    # Prueba 5: Filtros combinados
    filters = {
        'state': 'closed',
        'item_type': 'Issue'
    }
    filtered = analytics.filter_data(test_data, filters)
    print(f"✅ Filtros combinados (closed + Issue): {len(filtered)} elementos")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de correcciones de Analytics...\n")
    
    # Verificar que estamos en el directorio correcto
    current_dir = os.getcwd()
    print(f"📂 Directorio actual: {current_dir}")
    
    # Verificar que tenemos las dependencias
    try:
        import matplotlib
        import seaborn  
        import plotly
        import pandas
        import numpy
        print("✅ Todas las dependencias están disponibles")
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("💡 Ejecute: pip install -r requirements.txt")
        sys.exit(1)
    
    # Ejecutar pruebas
    try:
        success = test_analytics_functionality()
        if success:
            test_filter_functionality()
            print("\n🎯 ¡Todas las correcciones están funcionando correctamente!")
        else:
            print("\n❌ Algunas pruebas fallaron. Revise los errores anteriores.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado durante las pruebas: {e}")
        sys.exit(1)
