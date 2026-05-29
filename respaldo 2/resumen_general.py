import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc
from dash import html

def obtener_metricas_globales():
    conn = sqlite3.connect('municipio.db')
    metricas = {}

    try:
        # 1. Metrica de Obra Pública (Inversión Total)
        df_obras = pd.read_sql_query("SELECT monto_total_invertido FROM proyectos", conn)
        df_obras['monto'] = pd.to_numeric(df_obras['monto_total_invertido'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
        metricas['obra_inversion'] = f"${df_obras['monto'].sum():,.2f}"
    except: metricas['obra_inversion'] = "$0.00"

    try:
        # 2. Metrica de Atención Ciudadana (Total personas)
        df_atencion = pd.read_sql_query("SELECT cantidad FROM atencion_ciudadana", conn)
        metricas['atencion_total'] = f"{int(df_atencion['cantidad'].sum()):,}"
    except: metricas['atencion_total'] = "0"

    try:
        # 3. Metrica de Deporte/COMUDE (Eventos o Participantes)
        df_comude = pd.read_sql_query("SELECT cantidad FROM deportes", conn)
        metricas['deporte_total'] = f"{int(df_comude['cantidad'].sum()):,}"
    except: metricas['deporte_total'] = "0"

    conn.close()
    return metricas

def layout_resumen():
    m = obtener_metricas_globales()
    
    return html.Div([
        html.H3("📊 ESTADO GENERAL DEL MUNICIPIO", className="text-center mb-4", style={'color': '#691c32', 'fontWeight': 'bold'}),
        dbc.Row([
            # Tarjeta Obra Pública
            crear_tarjeta_resumen("INVERSIÓN EN OBRA", m['obra_inversion'], "bi-cone-striped", "#1a472a"),
            # Tarjeta Atención
            crear_tarjeta_resumen("CIUDADANOS ATENDIDOS", m['atencion_total'], "bi-people-fill", "#bc955c"),
            # Tarjeta COMUDE
            crear_tarjeta_resumen("IMPACTO DEPORTIVO", m['deporte_total'], "bi-trophy-fill", "#691c32"),
        ], className="justify-content-center")
    ])

def crear_tarjeta_resumen(titulo, valor, icono, color):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className=f"{icono} h1", style={'color': color}),
                    html.H5(titulo, className="card-title text-muted mt-2"),
                    html.H2(valor, style={'color': color, 'fontWeight': 'black'})
                ], className="text-center")
            ])
        ], className="shadow-sm border-0 m-2", style={'borderTop': f'6px solid {color}', 'minWidth': '250px'}),
        width="auto"
    )
