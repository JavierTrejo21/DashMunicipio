import dash_bootstrap_components as dbc
from dash import html

def analizar_adultos_mayores(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Atención a Adultos Mayores llegó vacío.", color="warning", className="m-3")
    
    return html.Div([
        html.H4("👵👴 Módulo de Atención a Adultos Mayores", style={"color": "#781d37", "fontWeight": "bold"}),
        html.P(f"Total de registros cargados: {len(df)}")
    ])
