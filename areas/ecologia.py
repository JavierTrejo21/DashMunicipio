import dash_bootstrap_components as dbc
from dash import html

def analizar_ecologia(df):
    # Imprime en la terminal para verificar si los datos están llegando
    print(f"DEBUG ECOLOGÍA - Filas recibidas: {len(df) if df is not None else 'Es None'}")
    
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Ecología llegó vacío al módulo.", color="warning", className="m-3")
    
    return html.Div([
        html.H4("🌱 Módulo de Ecología y Medio Ambiente", style={"color": "#781d37", "fontWeight": "bold"}),
        html.P(f"Total de registros procesados: {len(df)}")
    ])
