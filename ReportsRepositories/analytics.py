"""
Módulo de análisis y visualización de datos para GitHub Reports
Contiene funciones para generar gráficos, estadísticas y análisis avanzados
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime, timedelta
import os
from collections import Counter
import re

# Configurar estilo para matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class GitHubAnalytics:
    def __init__(self, data=None):
        """
        Inicializa el analizador con datos de issues y PRs
        Args:
            data: Lista de diccionarios con información de issues/PRs (opcional)
        """
        self.df = None
        if data:
            self.df = self.prepare_data(data)
    
    def prepare_data(self, data=None):
        """Prepara y limpia los datos para análisis"""
        if data is None and self.df is None:
            return pd.DataFrame()
        
        if data:
            df = pd.DataFrame(data)
        else:
            df = self.df.copy() if self.df is not None else pd.DataFrame()
        
        if df.empty:
            return df
        
        # Mapear nombres de columnas para compatibilidad
        column_mapping = {
            'Fecha_Creacion': 'Creado',
            'Fecha_Cerrado': 'Cerrado',
            'Autor': 'Autor',
            'Estado': 'Estado',
            'Tipo': 'Tipo',
            'Etiquetas': 'Etiquetas',
            'Título': 'Titulo',
            'Descripción': 'Descripcion'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        
        # Convertir fechas a datetime (sin timezone para compatibilidad con Excel)
        if 'Creado' in df.columns:
            df['Creado'] = pd.to_datetime(df['Creado'], errors='coerce', utc=True).dt.tz_localize(None)
        if 'Cerrado' in df.columns:
            df['Cerrado'] = pd.to_datetime(df['Cerrado'], errors='coerce', utc=True).dt.tz_localize(None)
        
        # Calcular tiempo de resolución en días
        if 'Creado' in df.columns and 'Cerrado' in df.columns:
            df['Tiempo_Resolucion'] = (df['Cerrado'] - df['Creado']).dt.days
        
        # Extraer mes y año para agrupaciones
        if 'Creado' in df.columns:
            df['Mes_Año'] = df['Creado'].dt.to_period('M')
            df['Año'] = df['Creado'].dt.year
        
        # Procesar etiquetas (labels)
        if not df.empty:
            df['Etiquetas_Lista'] = df.apply(self._extraer_etiquetas, axis=1)
            
            # Procesar autores de commits
            if 'Autores Commits' in df.columns:
                df['Autores_Lista'] = df['Autores Commits'].apply(self._procesar_autores)
            elif 'Autor' in df.columns:
                df['Autores_Lista'] = df['Autor'].apply(lambda x: [x] if pd.notna(x) else [])
            else:
                df['Autores_Lista'] = [[] for _ in range(len(df))]
        
        return df
    
    def _extraer_etiquetas(self, row):
        """Extrae etiquetas del título o descripción"""
        etiquetas = []
        
        # Verificar si existe la columna Etiquetas primero
        if 'Etiquetas' in row and pd.notna(row['Etiquetas']) and row['Etiquetas']:
            # Si hay etiquetas explícitas, usarlas
            if isinstance(row['Etiquetas'], str):
                etiquetas = [tag.strip() for tag in row['Etiquetas'].split(',') if tag.strip()]
            elif isinstance(row['Etiquetas'], list):
                etiquetas = row['Etiquetas']
        
        # Si no hay etiquetas explícitas, buscar en título y descripción
        if not etiquetas:
            titulo = row.get('Titulo', '') or row.get('Título', '') or ''
            descripcion = row.get('Descripcion', '') or row.get('Descripción', '') or ''
            texto = f"{titulo} {descripcion}".lower()
            
            # Buscar etiquetas comunes
            etiquetas_comunes = ['bug', 'feature', 'enhancement', 'documentation', 
                               'help wanted', 'good first issue', 'question', 
                               'wontfix', 'duplicate', 'invalid', 'security',
                               'performance', 'ui', 'ux', 'api', 'test', 'refactor']
            
            for etiqueta in etiquetas_comunes:
                if etiqueta in texto:
                    etiquetas.append(etiqueta)
        
        return etiquetas if etiquetas else ['sin etiqueta']
    
    def _procesar_autores(self, autores_str):
        """Procesa la cadena de autores y devuelve una lista"""
        if pd.isna(autores_str) or autores_str == "Ninguno":
            return []
        return [autor.strip() for autor in autores_str.split(',')]
    
    def generar_dashboard_html(self, output_dir="reportes"):
        """Genera un dashboard HTML completo con todos los gráficos"""
        if self.df.empty:
            return None
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar todos los gráficos
        fig_tendencias = self.grafico_tendencias_mensual()
        fig_contribuidores = self.grafico_contribuidores_activos()
        fig_tiempo_resolucion = self.grafico_tiempo_resolucion()
        fig_etiquetas = self.grafico_etiquetas_populares()
        fig_estados = self.grafico_distribucion_estados()
        fig_tipos = self.grafico_tipos_issues_prs()
        
        # Crear dashboard combinado
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard GitHub Analytics</title>
            <meta charset="utf-8">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .chart-container {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .full-width {{
                    grid-column: 1 / -1;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;
                }}
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }}
                .stat-label {{
                    color: #666;
                    margin-top: 5px;
                }}
                h2 {{
                    color: #333;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Dashboard de Análisis GitHub</h1>
                    <p>Análisis completo de issues y pull requests</p>
                    <p>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                {self._generar_estadisticas_resumen()}
                
                <div class="grid">
                    <div class="chart-container full-width">
                        <h2>📈 Tendencias Mensuales</h2>
                        <div id="tendencias">{fig_tendencias.to_html(include_plotlyjs=False, div_id="tendencias")}</div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>👥 Contribuidores Más Activos</h2>
                        <div id="contribuidores">{fig_contribuidores.to_html(include_plotlyjs=False, div_id="contribuidores")}</div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>⏱️ Tiempo de Resolución</h2>
                        <div id="tiempo">{fig_tiempo_resolucion.to_html(include_plotlyjs=False, div_id="tiempo")}</div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>🏷️ Etiquetas Más Populares</h2>
                        <div id="etiquetas">{fig_etiquetas.to_html(include_plotlyjs=False, div_id="etiquetas")}</div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>📊 Distribución de Estados</h2>
                        <div id="estados">{fig_estados.to_html(include_plotlyjs=False, div_id="estados")}</div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>📋 Issues vs Pull Requests</h2>
                        <div id="tipos">{fig_tipos.to_html(include_plotlyjs=False, div_id="tipos")}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Guardar dashboard
        dashboard_path = os.path.join(output_dir, "github_analytics_dashboard.html")
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        return dashboard_path
    
    def _generar_estadisticas_resumen(self):
        """Genera las estadísticas de resumen para el dashboard"""
        total_items = len(self.df)
        issues_abiertos = len(self.df[(self.df['Tipo'] == 'Issue') & (self.df['Estado'] == 'open')])
        prs_abiertos = len(self.df[(self.df['Tipo'] == 'Pull Request') & (self.df['Estado'] == 'open')])
        
        # Tiempo promedio de resolución
        tiempo_promedio = self.df[self.df['Estado'] == 'closed']['Tiempo_Resolucion'].mean()
        tiempo_promedio = f"{tiempo_promedio:.1f}" if not pd.isna(tiempo_promedio) else "N/A"
        
        # Contribuidor más activo
        todos_autores = []
        for autores_lista in self.df['Autores_Lista']:
            todos_autores.extend(autores_lista)
        contribuidor_top = Counter(todos_autores).most_common(1)
        contribuidor_top = contribuidor_top[0][0] if contribuidor_top else "N/A"
        
        return f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_items}</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{issues_abiertos}</div>
                <div class="stat-label">Issues Abiertos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{prs_abiertos}</div>
                <div class="stat-label">PRs Abiertos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{tiempo_promedio}</div>
                <div class="stat-label">Días Promedio Resolución</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{contribuidor_top}</div>
                <div class="stat-label">Top Contribuidor</div>
            </div>
        </div>
        """
    
    def grafico_tendencias_mensual(self):
        """Genera gráfico de tendencias mensuales de issues y PRs"""
        if self.df.empty:
            return go.Figure()
        
        # Agrupar por mes y tipo
        tendencias = self.df.groupby(['Mes_Año', 'Tipo']).size().unstack(fill_value=0)
        
        fig = go.Figure()
        
        # Agregar líneas para cada tipo
        if 'Issue' in tendencias.columns:
            fig.add_trace(go.Scatter(
                x=tendencias.index.astype(str),
                y=tendencias['Issue'],
                mode='lines+markers',
                name='Issues',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8)
            ))
        
        if 'Pull Request' in tendencias.columns:
            fig.add_trace(go.Scatter(
                x=tendencias.index.astype(str),
                y=tendencias['Pull Request'],
                mode='lines+markers',
                name='Pull Requests',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Tendencias Mensuales de Issues y PRs",
            xaxis_title="Mes",
            yaxis_title="Cantidad",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def grafico_contribuidores_activos(self, top_n=10):
        """Genera gráfico de contribuidores más activos"""
        if self.df.empty:
            return go.Figure()
        
        # Obtener todos los autores
        todos_autores = []
        for autores_lista in self.df['Autores_Lista']:
            todos_autores.extend(autores_lista)
        
        if not todos_autores:
            return go.Figure()
        
        # Contar contribuciones
        contribuciones = Counter(todos_autores).most_common(top_n)
        
        autores = [item[0] for item in contribuciones]
        counts = [item[1] for item in contribuciones]
        
        fig = go.Figure(data=[
            go.Bar(
                x=autores,
                y=counts,
                text=counts,
                textposition='auto',
                marker_color=px.colors.qualitative.Set3[:len(autores)]
            )
        ])
        
        fig.update_layout(
            title=f"Top {top_n} Contribuidores Más Activos",
            xaxis_title="Contribuidores",
            yaxis_title="Número de Contribuciones",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def grafico_tiempo_resolucion(self):
        """Genera gráfico de distribución de tiempo de resolución"""
        if self.df.empty:
            return go.Figure()
        
        # Filtrar solo items cerrados con tiempo válido
        cerrados = self.df[(self.df['Estado'] == 'closed') & 
                          (self.df['Tiempo_Resolucion'].notna()) &
                          (self.df['Tiempo_Resolucion'] >= 0)]
        
        if cerrados.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Histograma para Issues
        issues_cerrados = cerrados[cerrados['Tipo'] == 'Issue']['Tiempo_Resolucion']
        if not issues_cerrados.empty:
            fig.add_trace(go.Histogram(
                x=issues_cerrados,
                name='Issues',
                opacity=0.7,
                marker_color='#e74c3c',
                nbinsx=20
            ))
        
        # Histograma para PRs
        prs_cerrados = cerrados[cerrados['Tipo'] == 'Pull Request']['Tiempo_Resolucion']
        if not prs_cerrados.empty:
            fig.add_trace(go.Histogram(
                x=prs_cerrados,
                name='Pull Requests',
                opacity=0.7,
                marker_color='#3498db',
                nbinsx=20
            ))
        
        fig.update_layout(
            title="Distribución de Tiempo de Resolución",
            xaxis_title="Días para Resolución",
            yaxis_title="Frecuencia",
            barmode='overlay',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def grafico_etiquetas_populares(self, top_n=10):
        """Genera gráfico de etiquetas más populares"""
        if self.df.empty:
            return go.Figure()
        
        # Obtener todas las etiquetas
        todas_etiquetas = []
        for etiquetas_lista in self.df['Etiquetas_Lista']:
            todas_etiquetas.extend(etiquetas_lista)
        
        if not todas_etiquetas:
            return go.Figure()
        
        # Contar etiquetas
        etiquetas_count = Counter(todas_etiquetas).most_common(top_n)
        
        etiquetas = [item[0] for item in etiquetas_count]
        counts = [item[1] for item in etiquetas_count]
        
        fig = go.Figure(data=[
            go.Bar(
                y=etiquetas,
                x=counts,
                orientation='h',
                text=counts,
                textposition='auto',
                marker_color=px.colors.qualitative.Pastel[:len(etiquetas)]
            )
        ])
        
        fig.update_layout(
            title=f"Top {top_n} Etiquetas Más Populares",
            xaxis_title="Frecuencia",
            yaxis_title="Etiquetas",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def grafico_distribucion_estados(self):
        """Genera gráfico de distribución de estados"""
        if self.df.empty:
            return go.Figure()
        
        estados = self.df['Estado'].value_counts()
        
        colors = ['#27ae60', '#e74c3c']  # Verde para open, rojo para closed
        
        fig = go.Figure(data=[
            go.Pie(
                labels=estados.index,
                values=estados.values,
                hole=0.4,
                marker_colors=colors[:len(estados)]
            )
        ])
        
        fig.update_layout(
            title="Distribución de Estados (Abierto vs Cerrado)",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def grafico_tipos_issues_prs(self):
        """Genera gráfico de distribución entre Issues y PRs"""
        if self.df.empty:
            return go.Figure()
        
        tipos = self.df['Tipo'].value_counts()
        
        colors = ['#9b59b6', '#f39c12']  # Púrpura para Issues, naranja para PRs
        
        fig = go.Figure(data=[
            go.Pie(
                labels=tipos.index,
                values=tipos.values,
                hole=0.4,
                marker_colors=colors[:len(tipos)]
            )
        ])
        
        fig.update_layout(
            title="Distribución: Issues vs Pull Requests",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def filter_data(self, data, filters):
        """Filtrar datos según criterios especificados"""
        # Preparar DataFrame si es necesario
        if self.df is None or self.df.empty:
            self.df = self.prepare_data(data)
        
        df_filtrado = self.df.copy()
        
        # Aplicar filtros
        if 'start_date' in filters:
            fecha_inicio = pd.to_datetime(filters['start_date'])
            df_filtrado = df_filtrado[df_filtrado['Creado'] >= fecha_inicio]
        
        if 'end_date' in filters:
            fecha_fin = pd.to_datetime(filters['end_date'])
            df_filtrado = df_filtrado[df_filtrado['Creado'] <= fecha_fin]
        
        if 'author' in filters:
            autor = filters['author']
            mask = df_filtrado['Autores_Lista'].apply(
                lambda x: any(autor.lower() in str(a).lower() for a in x) if x else False
            )
            df_filtrado = df_filtrado[mask]
        
        if 'labels' in filters:
            etiqueta = filters['labels']
            mask = df_filtrado['Etiquetas_Lista'].apply(
                lambda x: any(etiqueta.lower() in str(e).lower() for e in x) if x else False
            )
            df_filtrado = df_filtrado[mask]
        
        if 'state' in filters:
            estado = filters['state']
            df_filtrado = df_filtrado[df_filtrado['Estado'] == estado]
        
        if 'item_type' in filters:
            tipo = filters['item_type']
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo]
        
        if 'search_text' in filters:
            busqueda = filters['search_text']
            titulo_col = 'Titulo' if 'Titulo' in df_filtrado.columns else 'Título'
            desc_col = 'Descripcion' if 'Descripcion' in df_filtrado.columns else 'Descripción'
            
            mask = pd.Series([False] * len(df_filtrado))
            if titulo_col in df_filtrado.columns:
                mask |= df_filtrado[titulo_col].str.contains(busqueda, case=False, na=False)
            if desc_col in df_filtrado.columns:
                mask |= df_filtrado[desc_col].str.contains(busqueda, case=False, na=False)
            
            df_filtrado = df_filtrado[mask]
        
        return df_filtrado.to_dict('records')
    
    def export_filtered_data(self, filtered_data, output_dir):
        """Exportar datos filtrados a Excel"""
        if not filtered_data:
            return None
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"datos_filtrados_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        df = pd.DataFrame(filtered_data)
        
        # Convertir fechas con timezone a naive datetime para Excel
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns, UTC]' or str(df[col].dtype).startswith('datetime64[ns'):
                df[col] = pd.to_datetime(df[col], utc=True).dt.tz_localize(None)
        
        df.to_excel(filepath, index=False)
        
        return filepath
    
    def generate_dashboard(self, data, output_dir, repo_name):
        """Método principal para generar dashboard"""
        # Preparar datos si no están preparados
        if self.df is None or self.df.empty:
            self.df = self.prepare_data(data)
        
        # Generar dashboard HTML
        dashboard_path = self.generar_dashboard_html(output_dir)
        return dashboard_path
    
    def obtener_estadisticas_resumen(self):
        """Obtiene estadísticas de resumen de los datos"""
        if self.df.empty:
            return {}
        
        # Estadísticas generales
        total_items = len(self.df)
        total_issues = len(self.df[self.df['Tipo'] == 'Issue'])
        total_prs = len(self.df[self.df['Tipo'] == 'Pull Request'])
        
        issues_abiertos = len(self.df[(self.df['Tipo'] == 'Issue') & (self.df['Estado'] == 'open')])
        issues_cerrados = len(self.df[(self.df['Tipo'] == 'Issue') & (self.df['Estado'] == 'closed')])
        prs_abiertos = len(self.df[(self.df['Tipo'] == 'Pull Request') & (self.df['Estado'] == 'open')])
        prs_cerrados = len(self.df[(self.df['Tipo'] == 'Pull Request') & (self.df['Estado'] == 'closed')])
          # Tiempo de resolución (solo si la columna existe)
        tiempo_promedio = 0
        tiempo_mediano = 0
        if 'Tiempo_Resolucion' in self.df.columns:
            cerrados = self.df[(self.df['Estado'] == 'closed') & (self.df['Tiempo_Resolucion'].notna())]
            tiempo_promedio = cerrados['Tiempo_Resolucion'].mean() if not cerrados.empty else 0
            tiempo_mediano = cerrados['Tiempo_Resolucion'].median() if not cerrados.empty else 0
          # Contribuidores únicos
        todos_autores = []
        if 'Autores_Lista' in self.df.columns:
            for autores_lista in self.df['Autores_Lista']:
                if autores_lista:  # Verificar que no sea None o vacío
                    todos_autores.extend(autores_lista)
        contribuidores_unicos = len(set(todos_autores)) if todos_autores else 0
          # Período de datos
        fecha_min = self.df['Creado'].min() if 'Creado' in self.df.columns else None
        fecha_max = self.df['Creado'].max() if 'Creado' in self.df.columns else None
        
        return {
            'total_items': total_items,
            'total_issues': total_issues,
            'total_prs': total_prs,
            'issues_abiertos': issues_abiertos,
            'issues_cerrados': issues_cerrados,
            'prs_abiertos': prs_abiertos,
            'prs_cerrados': prs_cerrados,
            'tiempo_promedio_resolucion': round(tiempo_promedio, 1) if tiempo_promedio else 0,
            'tiempo_mediano_resolucion': round(tiempo_mediano, 1) if tiempo_mediano else 0,
            'contribuidores_unicos': contribuidores_unicos,
            'fecha_min': fecha_min.strftime('%Y-%m-%d') if fecha_min else None,
            'fecha_max': fecha_max.strftime('%Y-%m-%d') if fecha_max else None,
            'periodo_dias': (fecha_max - fecha_min).days if fecha_min and fecha_max else 0
        }
