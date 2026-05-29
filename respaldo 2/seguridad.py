import dash_bootstrap_components as dbc
from dash import html

def layout_seguridad():
    return dbc.Container([
        html.H2("🛡️ MÓDULO DE SEGURIDAD PÚBLICA", style={"color": "#691c32"}),
        html.P("Reportes de incidentes y vigilancia."),
        dbc.Alert("Este módulo está en proceso de carga de datos.", color="info")
    ], className="p-4")
