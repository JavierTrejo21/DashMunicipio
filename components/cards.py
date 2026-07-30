import dash_bootstrap_components as dbc
from dash import html

def crear_resumen_area_visual(titulo_area, texto_resumen, texto_objetivo):
    """
    Recibe el texto plano y genera el bloque contenedor estilizado 
    para el Resumen Estratégico y Objetivo General.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.I(className="bi bi-pin-angle-fill me-2", style={"color": "#691C32"}),
                    html.Span(f"RESUMEN ESTRATÉGICO: {titulo_area}", className="section-label"),
                ],
                className="mb-2 d-flex align-items-center"
            ),
            html.P(texto_resumen, className="text-muted mb-2", style={"fontSize": "0.85rem"}),
            html.Div(
                [
                    html.I(className="bi bi-bullseye me-2", style={"color": "#0D9488"}),
                    html.Span(f"OBJETIVO GENERAL: {texto_objetivo}", style={"fontSize": "0.82rem", "fontWeight": "600"}),
                ],
                className="d-flex align-items-center text-dark"
            )
        ],
        className="card-executive"
    )

def crear_boton_matriz_general():
    """Genera el botón centrado para la Matriz MIR General"""
    return html.Div(
        dbc.Button(
            [
                html.I(className="bi bi-bar-chart-line-fill me-2"),
                "VER MATRIZ MIR GENERAL (ALTA DIRECCIÓN)"
            ],
            outline=True,
            color="secondary",
            className="w-100 py-2 border-secondary-subtle fw-bold text-secondary",
            style={"fontSize": "0.85rem", "borderRadius": "8px"}
        ),
        className="my-3"
    )
