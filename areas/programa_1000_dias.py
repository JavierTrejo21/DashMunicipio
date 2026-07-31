import dash_bootstrap_components as dbc
from dash import html

def analizar_programa_1000_dias(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame del Programa 1000 Días llegó vacío.", color="warning", className="m-3")
    
    return html.Div([
        html.H4("🍼 Módulo de DIF Programa 1000 Días", style={"color": "#781d37", "fontWeight": "bold"}),
        html.P(f"Total de registros cargados: {len(df)}")
    ])
