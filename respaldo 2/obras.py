import dash_bootstrap_components as dbc
from dash import html

def layout_obras():
    return dbc.Container([
        html.H2("🏗️ INFRAESTRUCTURA Y OBRAS PÚBLICAS", style={"color": "#691c32"}),
        html.P("Seguimiento de proyectos y licitaciones."),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody("Obras en proceso: 0"), color="light"), md=4),
        ])
    ], className="p-4")
