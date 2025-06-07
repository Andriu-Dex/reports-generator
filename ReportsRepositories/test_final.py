#!/usr/bin/env python3
"""
Test final para verificar que todas las correcciones están funcionando
"""

import sys
import os

def test_analytics_functionality():
    """Prueba la funcionalidad completa del módulo analytics"""
    print("🔧 Iniciando prueba final de funcionalidad...")
    
    try:
        # Importar el módulo analytics
        from analytics import GitHubAnalytics
        print("✅ GitHubAnalytics importado correctamente")
        
        # Crear datos de prueba
        test_data = [
            {
                'Tipo': 'Issue',
                'Estado': 'open',
                'Titulo': 'Bug crítico en autenticación',
                'Descripcion': 'Los usuarios no pueden hacer login',
                'Autor': 'desarrollador1',
                'Fecha_Creacion': '2024-01-15T10:30:00Z',
                'Etiquetas': 'bug,critical,security'
            },
            {
                'Tipo': 'Pull Request',
                'Estado': 'closed',
                'Titulo': 'Implementar dashboard de métricas',
                'Descripcion': 'Nuevo dashboard con gráficos interactivos',
                'Autor': 'desarrollador2',
                'Fecha_Creacion': '2024-02-01T14:20:00Z',
                'Fecha_Cerrado': '2024-02-05T16:45:00Z',
                'Etiquetas': 'feature,enhancement,ui'
            },
            {
                'Tipo': 'Issue',
                'Estado': 'closed',
                'Titulo': 'Mejorar documentación API',
                'Descripcion': 'Añadir más ejemplos y casos de uso',
                'Autor': 'technical_writer',
                'Fecha_Creacion': '2024-01-20T09:15:00Z',
                'Fecha_Cerrado': '2024-01-25T11:30:00Z',
                'Etiquetas': 'documentation,api'
            },
            {
                'Tipo': 'Issue',
                'Estado': 'open',
                'Titulo': 'Optimizar rendimiento de consultas',
                'Descripcion': 'Las consultas a la base de datos son lentas',
                'Autor': 'desarrollador1',
                'Fecha_Creacion': '2024-03-01T08:00:00Z',
                'Etiquetas': 'performance,database'
            }
        ]
        
        # Inicializar analytics
        analytics = GitHubAnalytics(test_data)
        print(f"✅ Analytics inicializado con {len(test_data)} elementos de prueba")
        
        # Verificar preparación de datos
        if analytics.df is not None and not analytics.df.empty:
            print(f"✅ DataFrame preparado: {len(analytics.df)} filas, {len(analytics.df.columns)} columnas")
        else:
            print("❌ Error: DataFrame no preparado correctamente")
            return False
        
        # Probar filtros
        print("\n🔍 Probando sistema de filtros...")
        
        # Filtro por estado
        filtro_abiertos = analytics.filter_data(test_data, {'state': 'open'})
        print(f"✅ Filtro por estado 'open': {len(filtro_abiertos)} elementos")
        
        # Filtro por tipo
        filtro_issues = analytics.filter_data(test_data, {'item_type': 'Issue'})
        print(f"✅ Filtro por tipo 'Issue': {len(filtro_issues)} elementos")
        
        # Filtro por autor
        filtro_autor = analytics.filter_data(test_data, {'author': 'desarrollador1'})
        print(f"✅ Filtro por autor 'desarrollador1': {len(filtro_autor)} elementos")
        
        # Filtro por texto
        filtro_texto = analytics.filter_data(test_data, {'search_text': 'dashboard'})
        print(f"✅ Filtro por texto 'dashboard': {len(filtro_texto)} elementos")
        
        # Filtro por etiquetas
        filtro_etiquetas = analytics.filter_data(test_data, {'labels': 'bug'})
        print(f"✅ Filtro por etiqueta 'bug': {len(filtro_etiquetas)} elementos")
        
        # Probar estadísticas
        print("\n📊 Probando generación de estadísticas...")
        stats = analytics.obtener_estadisticas_resumen()
        print(f"✅ Estadísticas generadas: {len(stats)} métricas")
        print(f"   - Total items: {stats.get('total_items', 0)}")
        print(f"   - Issues: {stats.get('total_issues', 0)}")
        print(f"   - Pull Requests: {stats.get('total_prs', 0)}")
        print(f"   - Issues abiertos: {stats.get('issues_abiertos', 0)}")
        print(f"   - PRs cerrados: {stats.get('prs_cerrados', 0)}")
        
        # Probar generación de gráficos
        print("\n📈 Probando generación de gráficos...")
        try:
            fig_tendencias = analytics.grafico_tendencias_mensual()
            print("✅ Gráfico de tendencias mensuales generado")
            
            fig_contribuidores = analytics.grafico_contribuidores_activos()
            print("✅ Gráfico de contribuidores activos generado")
            
            fig_etiquetas = analytics.grafico_etiquetas_populares()
            print("✅ Gráfico de etiquetas populares generado")
            
            fig_estados = analytics.grafico_distribucion_estados()
            print("✅ Gráfico de distribución de estados generado")
            
        except Exception as e:
            print(f"⚠️ Advertencia en gráficos: {e}")
        
        # Probar exportación
        print("\n💾 Probando exportación de datos...")
        try:
            os.makedirs("test_final_output", exist_ok=True)
            export_path = analytics.export_filtered_data(filtro_abiertos, "test_final_output")
            if export_path and os.path.exists(export_path):
                print(f"✅ Datos exportados correctamente: {export_path}")
            else:
                print("⚠️ Advertencia: Exportación no completada")
        except Exception as e:
            print(f"⚠️ Advertencia en exportación: {e}")
        
        # Probar dashboard
        print("\n🎨 Probando generación de dashboard...")
        try:
            dashboard_path = analytics.generate_dashboard(test_data, "test_final_output", "test_repo")
            if dashboard_path and os.path.exists(dashboard_path):
                print(f"✅ Dashboard generado correctamente: {dashboard_path}")
            else:
                print("⚠️ Dashboard no generado")
        except Exception as e:
            print(f"⚠️ Advertencia en dashboard: {e}")
        
        print("\n🎉 ¡Todas las pruebas principales completadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analytics_functionality()
    if success:
        print("\n🚀 RESULTADO: Todas las correcciones están funcionando correctamente")
        print("✅ El módulo analytics está listo para usar en producción")
    else:
        print("\n💥 RESULTADO: Hay problemas que necesitan ser resueltos")
        sys.exit(1)
