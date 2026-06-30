# pbr_modules/mujeres.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px

def calcular_pbr_mujeres(df):
    """Módulo Especialista PbR: Instancia Municipal para el Desarrollo de las Mujeres"""
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().upper() for c in df_clean.columns]
    
    # --- LIMPIEZA AGRESIVA Y CONVERSIÓN NUMÉRICA BLINDADA ---
    # Si existen las columnas, les quitamos el signo '$', las comas, espacios y forzamos a número
    if 'INVERSION' in df_clean.columns:
        df_clean['INVERSION'] = df_clean['INVERSION'].astype(str).str.replace('$', '', regex=False)
        df_clean['INVERSION'] = df_clean['INVERSION'].str.replace(',', '', regex=False).str.strip()
        df_clean['INVERSION'] = pd.to_numeric(df_clean['INVERSION'], errors='coerce').fillna(0)
        
    if 'ATENDIDOS' in df_clean.columns:
        df_clean['ATENDIDOS'] = df_clean['ATENDIDOS'].astype(str).str.replace(',', '', regex=False).str.strip()
        df_clean['ATENDIDOS'] = pd.to_numeric(df_clean['ATENDIDOS'], errors='coerce').fillna(0)

    # Ahora que los datos son puramente numéricos, las operaciones matemáticas son 100% seguras
    inversion = df_clean['INVERSION'].sum() if 'INVERSION' in df_clean.columns else 0
    atendidas = df_clean['ATENDIDOS'].sum() if 'ATENDIDOS' in df_clean.columns else 0
    
    # Cálculo seguro del costo unitario
    costo_unitario = round(inversion / atendidas, 2) if atendidas > 0 else 0
    
    # Gráfica a la medida: Tipos de Variables Operativas de la Instancia
    if 'VARIABLE' in df_clean.columns and atendidas > 0:
        df_var = df_clean.groupby('VARIABLE').agg({'ATENDIDOS': 'sum'}).reset_index()
        fig = px.pie(df_var, values='ATENDIDOS', names='VARIABLE', hole=0.5, title="<b>Distribución del Impacto por Tipo de Servicio</b>")
        fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=200, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', title_font=dict(size=10, color="#1f2937"))
        fig.update_traces(textinfo='percent', marker=dict(colors=["#691c32", "#bc955c", "#7a1c32", "#e5e7eb"]))
        componente_grafica = dcc.Graph(figure=fig, config={'displayModeBar': False})
    else:
        componente_grafica = html.Div("No hay datos de variables suficientes para graficar.", className="text-muted text-center p-3", style={"fontSize": "0.75rem"})

    return html.Div([
        html.Div([
            html.Span("🟢 EVALUACIÓN DE EFICIENCIA - INSTANCIA DE LAS MUJERES", style={"fontWeight": "bold", "fontSize": "0.85rem", "color": "#1f2937"}),
            html.Span("Indicador de Rentabilidad Social", className="text-muted float-end", style={"fontSize": "0.7rem"})
        ], className="p-2 border-bottom mb-3 bg-light"),
        
        dbc.Row([
            dbc.Col(html.Div([
                html.Small("PRESUPUESTO ASIGNADO", className="text-muted d-block", style={"fontSize": "0.6rem"}),
                html.H5(f"${inversion:,.2f}" if inversion > 0 else "$ Gasto Corriente", style={"color": "#691c32", "fontWeight": "bold", "margin": "0"}),
                html.Small(f"Impacto en {int(atendidas):,} mujeres", className="text-muted", style={"fontSize": "0.55rem"})
            ], className="bg-white p-2 border text-center shadow-sm", style={"borderLeft": "4px solid #691c32"}), md=6),
            
            dbc.Col(html.Div([
                html.Small("INVERSIÓN POR CIUDADANA", className="text-muted d-block", style={"fontSize": "0.6rem"}),
                html.H5(f"${costo_unitario:,.2f}", style={"color": "#bc955c", "fontWeight": "bold", "margin": "0"}),
                html.Small("Costo promedio ponderado", className="text-muted", style={"fontSize": "0.55rem"})
            ], className="bg-white p-2 border text-center shadow-sm", style={"borderLeft": "4px solid #bc955c"}), md=6),
        ], className="mb-3"),
        
        componente_grafica
    ])
