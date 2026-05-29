import dash_bootstrap_components as dbc
from dash import html

def layout_inicio():
    return dbc.Container([
        html.Div(style={"textAlign": "center", "padding": "50px"}, children=[
            html.H1("SISTEMA DE MONITOREO MUNICIPAL", style={"color": "#691c32", "fontWeight": "bold"}),
            html.P("Bienvenido al panel de control administrativo.", className="lead"),
            html.Hr(),
            html.Img(src="https://via.placeholder.com/400x200?text=Logo+Municipio", style={"width": "300px"})
        ])
    ], fluid=True)
