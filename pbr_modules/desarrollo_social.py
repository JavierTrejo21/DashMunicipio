# pbr_modules/desarrollo_social.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px

def calcular_pbr_desarrollo_social(df):
    """Módulo Especialista PbR: Dirección de Desarrollo Social"""
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().upper() for c in df_clean.columns]
    
    totales = len(df_clean)
    # Filtro específico manual: En Desarrollo Social la meta se mide si ya fue 'Realizado'
    alcanzadas = len(df_clean[df_clean['VARIABLE'].str.contains("REALIZADO|APROBADO|CONFORMACI", na=False, case=False)])
    
    porcentaje = round((alcanzadas / totales) * 100, 1) if totales > 0 else 0
    
    # Lógica del Semáforo MIR
    if porcentaje >= 90:
        texto_semaforo, color_badge = "🟢 DESEMPEÑO ÓPTIMO", "#2ecc71"
    elif porcentaje >= 70:
        texto_semaforo, color_badge = "🟡 REZAGO MODERADO", "#f1c40f"
    else:
        texto_semaforo, color_badge = "🔴 ALERTA CRÍTICA", "#e74c3c"
        
    ciudadanos_impactados = df_clean['BENEFICIARIOS'].sum() if 'BENEFICIARIOS' in df_clean.columns else 0

    # Gráfica a la medida: Cobertura por Comunidad de Desarrollo Social
    df_comunidad = df_clean.groupby('COMUNIDAD').size().reset_index(name='Acciones').sort_values(by='Acciones').tail(7)
    fig = px.bar(df_comunidad, x='Acciones', y='COMUNIDAD', orientation='h', title="<b>Distribución de Programas Sociales por Comunidad</b>")
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title_font=dict(size=10, color="#1f2937"))
    fig.update_traces(marker_color="#691c32")

    return html.Div([
        html.Div([
            html.Span(f"{texto_semaforo} - DESARROLLO SOCIAL", style={"fontWeight": "bold", "fontSize": "0.85rem"}),
            html.Span("Evaluación Metodología MIR", className="text-muted float-end", style={"fontSize": "0.7rem"})
        ], className="p-2 border-bottom mb-3 bg-light"),
        
        dbc.Row([
            dbc.Col(html.Div([
                html.Small("EFICACIA OPERATIVA", className="text-muted d-block", style={"fontSize": "0.6rem"}),
                html.H5(f"{porcentaje}%", style={"color": color_badge, "fontWeight": "bold", "margin": "0"}),
                html.Small(f"{alcanzadas} de {totales} metas físicas", className="text-muted", style={"fontSize": "0.55rem"})
            ], className="bg-white p-2 border text-center shadow-sm", style={"borderLeft": f"4px solid {color_badge}"}), md=6),
            
            dbc.Col(html.Div([
                html.Small("COBERTURA CIUDADANA", className="text-muted d-block", style={"fontSize": "0.6rem"}),
                html.H5(f"{ciudadanos_impactados:,}", style={"color": "#691c32", "fontWeight": "bold", "margin": "0"}),
                html.Small("Beneficiarios acumulados", className="text-muted", style={"fontSize": "0.55rem"})
            ], className="bg-white p-2 border text-center shadow-sm", style={"borderLeft": "4px solid #691c32"}), md=6),
        ], className="mb-3"),
        
        dcc.Graph(figure=fig, config={'displayModeBar': False})
    ])
