#!/usr/bin/env python3
"""
Test script para verificar la funcionalidad de analytics
"""

import os
import sys
from datetime import datetime, timedelta
from analytics import GitHubAnalytics

def test_analytics():
    """Test básico de la funcionalidad de analytics"""
    print("🧪 Iniciando pruebas de Analytics...")
    
    # Crear datos de prueba
    sample_data = [
        {
            "Número": "1",
            "Título": "Fix critical bug",
            "Tipo": "Issue",
            "Estado": "closed",
            "Autor": "user1",
            "Fecha_Creacion": "2024-01-01T10:00:00Z",
            "Fecha_Cerrado": "2024-01-02T10:00:00Z",
            "Etiquetas": "bug,critical",
            "Descripción": "This is a critical bug that needs fixing"
        },
        {
            "Número": "2",
            "Título": "Add new feature",
            "Tipo": "Pull Request",
            "Estado": "open",
            "Autor": "user2",
            "Fecha_Creacion": "2024-01-05T10:00:00Z",
            "Fecha_Cerrado": None,
            "Etiquetas": "feature,enhancement",
            "Descripción": "Adding a new feature to improve functionality"
        },
        {
            "Número": "3",
            "Título": "Update documentation",
            "Tipo": "Issue",
            "Estado": "closed",
            "Autor": "user1",
            "Fecha_Creacion": "2024-01-03T10:00:00Z",
            "Fecha_Cerrado": "2024-01-04T10:00:00Z",
            "Etiquetas": "documentation",
            "Descripción": "Documentation needs to be updated"
        },
        {
            "Número": "4",
            "Título": "Performance improvement",
            "Tipo": "Pull Request",
            "Estado": "closed",
            "Autor": "user3",
            "Fecha_Creacion": "2024-01-06T10:00:00Z",
            "Fecha_Cerrado": "2024-01-07T10:00:00Z",
            "Etiquetas": "performance,optimization",
            "Descripción": "Improving application performance"
        }
    ]
    
    try:
        # Inicializar analytics sin datos
        analytics = GitHubAnalytics()
        print("✅ GitHubAnalytics inicializado correctamente")
        
        # Preparar datos
        df = analytics.prepare_data(sample_data)
        print(f"✅ Datos preparados: {len(df)} elementos")
        
        # Actualizar el objeto analytics con los datos
        analytics.df = df
        
        # Test filtros
        filters = {
            'state': 'closed',
            'item_type': 'Issue'
        }
        filtered_data = analytics.filter_data(sample_data, filters)
        print(f"✅ Filtros aplicados: {len(filtered_data)} elementos filtrados")
        
        # Test análisis de tendencias
        if not df.empty:
            monthly_trends = analytics.analyze_trends(df)
            print(f"✅ Análisis de tendencias: {len(monthly_trends)} períodos")
        
        # Test contribuyentes activos
        active_contributors = analytics.get_active_contributors(df)
        print(f"✅ Contribuyentes activos: {len(active_contributors)} usuarios")
        
        # Test tiempo de resolución
        resolution_times = analytics.analyze_resolution_time(df)
        if resolution_times is not None and len(resolution_times) > 0:
            print(f"✅ Análisis de tiempos de resolución: {len(resolution_times)} elementos")
        else:
            print("⚠️ No hay datos de tiempo de resolución")
        
        # Test etiquetas populares
        popular_tags = analytics.get_popular_tags(df)
        print(f"✅ Etiquetas populares: {len(popular_tags)} etiquetas")
        
        # Test exportación
        output_dir = os.path.join(os.path.dirname(__file__), "..", "reportes")
        os.makedirs(output_dir, exist_ok=True)
        
        export_path = analytics.export_filtered_data(filtered_data, output_dir)
        print(f"✅ Datos exportados a: {export_path}")
        
        # Test dashboard (sin abrir navegador)
        dashboard_path = analytics.generate_dashboard(
            sample_data, 
            output_dir, 
            "test/repo"
        )
        print(f"✅ Dashboard generado en: {dashboard_path}")
        
        print("\n🎉 Todas las pruebas completadas exitosamente!")
        print("\n📊 Resumen de funcionalidades probadas:")
        print("• ✅ Inicialización de Analytics")
        print("• ✅ Preparación de datos")
        print("• ✅ Sistema de filtros")
        print("• ✅ Análisis de tendencias")
        print("• ✅ Contribuyentes activos")
        print("• ✅ Tiempos de resolución")
        print("• ✅ Etiquetas populares")
        print("• ✅ Exportación de datos")
        print("• ✅ Generación de dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analytics()
    sys.exit(0 if success else 1)
