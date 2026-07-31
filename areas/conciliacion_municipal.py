import dash_bootstrap_components as dbc
from dash import html

def analizar_conciliacion_municipal(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Conciliación Municipal llegó vacío.", color="warning", className="m-3")
    
    return html.Div([
        html.H4("🤝 Módulo de Conciliación Municipal", style={"color": "#781d37", "fontWeight": "bold"}),
        html.P(f"Total de registros cargados: {len(df)}")
    ])
