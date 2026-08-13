# areas/programa_1000_dias.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA (misma que bibliotecas.py)
# ==========================================================
GUINDA = "#781D37"
GUINDA_DARK = "#54132A"
GUINDA_LIGHT = "#F3E7EB"
VERDE = "#1CA2A9"
VERDE_DARK = "#147880"
VERDE_LIGHT = "#E3F5F6"
BG = "#EFEDE6"
CARD = "#FFFFFF"
INK = "#241E1B"
INK_SOFT = "#6B625C"
INK_FAINT = "#9B928C"
LINE = "#E3DDD2"

FONT_SANS = "'Inter', sans-serif"
FONT_SERIF = "'Playfair Display', serif"

# Universo total de comunidades en el municipio
TOTAL_COMUNIDADES_MUNICIPIO = 73


# ==========================================================
# BLOQUES DE LAYOUT (idénticos a los usados en bibliotecas.py)
# ==========================================================

def _fuentes_e_iconos():
    return html.Div([
        html.Link(rel="preconnect", href="https://fonts.googleapis.com"),
        html.Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap"),
        html.Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css"),
    ])


def _section_label(icono, texto):
    return html.Div([
        html.I(className=f"ti {icono}", style={"color": VERDE, "fontSize": "16px"}),
        html.Span(texto, style={
            "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "14px",
            "letterSpacing": ".04em", "color": GUINDA_DARK, "textTransform": "uppercase", "whiteSpace": "nowrap"
        }),
        html.Div(style={"flex": "1", "height": "1px", "background": LINE}),
    ], style={"display": "flex", "alignItems": "center", "gap": "9px", "margin": "22px 0 16px"})


def _kpi_card(icono, eyebrow, valor, sub, color=VERDE):
    color_light = VERDE_LIGHT if color == VERDE else GUINDA_LIGHT
    color_dark = VERDE_DARK if color == VERDE else GUINDA_DARK
    return html.Div([
        html.Div([
            html.Div(
                html.Div(html.I(className=f"ti {icono}"), style={
                    "width": "100%", "height": "100%", "borderRadius": "50%", "background": color_light,
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "fontSize": "20px", "color": color_dark, "border": "1px solid #fff"
                }),
                style={
                    "width": "50px", "height": "50px", "borderRadius": "50%", "flexShrink": "0", "padding": "3px",
                    "background": f"conic-gradient({color} 100%, {LINE} 0)"
                }
            ),
            html.Div([
                html.Div(eyebrow, style={
                    "fontSize": "9.5px", "fontWeight": "700", "letterSpacing": ".08em",
                    "color": INK_FAINT, "textTransform": "uppercase", "marginBottom": "3px"
                }),
                html.Div(valor, style={"fontWeight": "700", "fontSize": "17px", "lineHeight": "1.25", "color": INK}),
                html.Div(sub, style={"fontSize": "10.5px", "color": INK_SOFT, "marginTop": "3px"}) if sub else None,
            ], style={"flex": "1", "minWidth": "0"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "14px"}),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px", "position": "relative",
        "padding": "18px 20px", "boxShadow": "0 1px 2px rgba(84,19,42,.05)",
        "borderTop": f"3px solid {color}", "height": "100%", "boxSizing": "border-box"
    })


def analizar_programa_1000_dias(df):
    """Módulo adaptado con tarjetas de resumen mejoradas e índice de cobertura municipal basado en las 73 comunidades totales."""

    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip().str.title()

    columnas_reales = df.columns.tolist()

    col_comunidad = next((c for c in columnas_reales if "COMUNIDAD" in str(c).upper()), "Comunidad")
    col_cantidad = next((c for c in columnas_reales if "CANTIDAD" in str(c).upper()), "Cantidad")
    col_mes = next((c for c in columnas_reales if "MES" in str(c).upper()), "Mes")

    df_limpio = pd.DataFrame()
    df_limpio['Comunidad'] = df[col_comunidad].astype(str).str.strip().str.title() if col_comunidad in df.columns else "General"
    df_limpio['Cantidad'] = pd.to_numeric(df[col_cantidad], errors='coerce').fillna(0) if col_cantidad in df.columns else 0
    df_limpio['Mes'] = df[col_mes].astype(str).str.strip().str.capitalize() if col_mes in df.columns else "General"

    total_apoyos = df_limpio['Cantidad'].sum()

    # Análisis de comunidades atendidas frente al universo real municipal (73)
    df_efectivo = df_limpio[df_limpio['Cantidad'] > 0].copy()
    comunidades_atendidas = df_efectivo['Comunidad'].nunique()

    # Cálculo real del Índice de Cobertura Municipal
    indice_cobertura_municipal = (comunidades_atendidas / TOTAL_COMUNIDADES_MUNICIPIO * 100) if TOTAL_COMUNIDADES_MUNICIPIO > 0 else 0

    # =================================================================
    # KPI CARDS (estilo institucional: badge-ring + borde superior)
    # =================================================================
    kpis_row = dbc.Row([
        dbc.Col(_kpi_card("ti-package", "Total de despensas entregadas", f"{int(total_apoyos):,} apoyos", "Acumulado histórico del periodo", VERDE), width=12, md=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-map-pin", "Localidades atendidas", f"{comunidades_atendidas} de {TOTAL_COMUNIDADES_MUNICIPIO}", "Comunidades con entrega activa", GUINDA), width=12, md=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-chart-pie", "Índice de cobertura municipal", f"{indice_cobertura_municipal:.1f}%", f"Sobre {TOTAL_COMUNIDADES_MUNICIPIO} localidades totales", VERDE), width=12, md=4, className="mb-3"),
    ])

    # =================================================================
    # TABLA CONSOLIDADA POR COMUNIDAD (scroll vertical)
    # =================================================================
    df_resumen_comunidad = df_efectivo.groupby('Comunidad')['Cantidad'].sum().reset_index()
    df_resumen_comunidad = df_resumen_comunidad.sort_values(by='Cantidad', ascending=False)

    th_style = {
        "fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
        "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
        "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}",
        "position": "sticky", "top": "0", "zIndex": "1"
    }
    td_style = {"fontSize": "12.5px", "color": INK, "padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}

    filas_tabla = []
    for i, (_, row) in enumerate(df_resumen_comunidad.iterrows()):
        bg = "#FAF8F4" if i % 2 == 1 else CARD
        filas_tabla.append(html.Tr([
            html.Td(row['Comunidad'], style={**td_style, "backgroundColor": bg, "fontWeight": "600"}),
            html.Td(f"{int(row['Cantidad']):,} despensas", style={**td_style, "backgroundColor": bg, "textAlign": "center", "fontWeight": "700", "color": GUINDA_DARK}),
        ])) if filas_tabla is not None else None

    if not filas_tabla:
        filas_tabla = [html.Tr([html.Td("Sin registros", colSpan=2, style={**td_style, "textAlign": "center", "color": INK_FAINT})])]

    fila_total = html.Tr([
        html.Td("TOTAL ACUMULADO DEL PERIODO", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
        html.Td(f"{int(total_apoyos):,} despensas", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": GUINDA, "textAlign": "center"}),
    ])

    tabla_consolidada = html.Div([
        # Encabezado fijo
        html.Table([
            html.Thead(html.Tr([
                html.Th("Comunidad / Localidad", style={**th_style, "width": "65%"}),
                html.Th("Total Acumulado", style={**th_style, "textAlign": "center", "width": "35%", "backgroundColor": GUINDA}),
            ])),
        ], style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
        # Cuerpo con scroll
        html.Div(
            html.Table([
                html.Tbody(filas_tabla)
            ], style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
            style={"maxHeight": "320px", "overflowY": "auto"}
        ),
        # Fila de totales siempre visible
        html.Table([
            html.Tbody([fila_total])
        ], style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {VERDE}", "overflow": "hidden"
    })

    # =================================================================
    # TARJETA DE CONTEXTO OPERATIVO
    # =================================================================
    card_info = html.Div([
        html.Div([
            html.I(className="ti ti-info-circle", style={"color": VERDE, "fontSize": "15px"}),
            html.Span("Detalles del programa", style={
                "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "13px",
                "letterSpacing": ".04em", "color": GUINDA_DARK, "textTransform": "uppercase"
            }),
        ], style={"display": "flex", "alignItems": "center", "gap": "8px",
                  "borderBottom": f"1px solid {LINE}", "paddingBottom": "10px", "marginBottom": "12px"}),
        html.P(
            "El Programa 1000 Días opera mediante la entrega continua de despensas destinadas a beneficiarios específicos en periodos establecidos.",
            style={"fontSize": "12.5px", "color": INK_SOFT, "lineHeight": "1.6", "marginBottom": "12px"}
        ),
        html.Ul([
            html.Li(f"Universo total municipal: {TOTAL_COMUNIDADES_MUNICIPIO} localidades registradas.",
                    style={"fontSize": "12px", "color": INK, "marginBottom": "6px"}),
            html.Li(f"Localidades atendidas efectivamente: {comunidades_atendidas}.",
                    style={"fontSize": "12px", "color": INK, "marginBottom": "6px"}),
            html.Li(f"Localidades pendientes de cobertura: {TOTAL_COMUNIDADES_MUNICIPIO - comunidades_atendidas}.",
                    style={"fontSize": "12px", "color": INK, "fontWeight": "600"}),
        ], style={"paddingLeft": "18px", "margin": "0"}),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {GUINDA}", "padding": "16px 20px",
        "boxShadow": "0 1px 2px rgba(84,19,42,.05)", "height": "100%", "boxSizing": "border-box"
    })

    # =================================================================
    # LAYOUT CONSOLIDADO FINAL
    # =================================================================
    return html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-chart-bar", "Resumen general"),
        kpis_row,
        _section_label("ti-table", "Consolidado de entregas por comunidad"),
        dbc.Row([
            dbc.Col(tabla_consolidada, md=7, className="mb-3"),
            dbc.Col(card_info, md=5, className="mb-3"),
        ]),
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})