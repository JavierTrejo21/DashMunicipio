import dash_bootstrap_components as dbc
from dash import html

def crear_header():
    """Genera la barra de navegación superior limpia"""
    return dbc.Navbar(
        dbc.Container(
            [
                html.Div(
                    "SISTEMA DE GESTIÓN MUNICIPAL | PBR - PMD",
                    className="fw-bold text-white",
                    style={"fontSize": "1.05rem", "letterSpacing": "0.5px"}
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("CONFIGURACIÓN", href="#", className="text-white-50 px-3 fs-7 fw-bold")),
                        dbc.NavItem(dbc.NavLink("ACTUALIZAR DATOS", href="#", className="text-white-50 px-3 fs-7 fw-bold")),
                        dbc.NavItem(dbc.NavLink("ELIMINAR SECCIÓN", href="#", className="text-white-50 px-3 fs-7 fw-bold")),
                    ],
                    className="ms-auto d-flex align-items-center",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="#691C32",
        dark=True,
        className="mb-4 shadow-sm py-2",
    )
