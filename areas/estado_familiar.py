import dash_bootstrap_components as dbc
from dash import html

def analizar_estado_familiar(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Registro del Estado Familiar llegó vacío.", color="warning", className="m-3")
    
    return html.Div([
        html.H4("💍 Módulo de Registro del Estado Familiar", style={"color": "#781d37", "fontWeight": "bold"}),
        html.P(f"Total de registros cargados: {len(df)}")
    ])
