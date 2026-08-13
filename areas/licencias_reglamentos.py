# areas/licencias_reglamentos.py
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA (igual que el HTML de referencia)
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

# ==========================================================
# DATOS PLANOS (idénticos a los del HTML de referencia)
# ==========================================================
ACTIVIDADES = [
    {"actividad": "Cobros de Piso", "cantidad": 25, "recaudacion": 32118.2, "clasificacion": "Permisos de uso de espacios públicos"},
    {"actividad": "Licencias para venta de Alcohol (Expedición/Renovación)", "cantidad": 49, "recaudacion": 29106.0, "clasificacion": "Trámites realizados"},
    {"actividad": "Placas de Funcionamiento", "cantidad": 15, "recaudacion": 9153.7, "clasificacion": "Trámites realizados"},
    {"actividad": "Auditorio Municipal", "cantidad": 24, "recaudacion": 8209.5, "clasificacion": "Permisos de uso de espacios públicos"},
    {"actividad": "Gavetas Construidas", "cantidad": 29, "recaudacion": 6525.2, "clasificacion": "Permisos fúnebres diversos"},
    {"actividad": "Inhumaciones", "cantidad": 26, "recaudacion": 3697.8, "clasificacion": "Permisos fúnebres diversos"},
    {"actividad": "Exhumaciones", "cantidad": 2, "recaudacion": 127.4, "clasificacion": "Permisos fúnebres diversos"},
    {"actividad": "Permisos - Cancha Techada", "cantidad": 33, "recaudacion": 0.0, "clasificacion": "Permisos de uso de espacios públicos"},
    {"actividad": "Permisos - Kiosko Municipal", "cantidad": 12, "recaudacion": 0.0, "clasificacion": "Permisos de uso de espacios públicos"},
]

MESES = ["Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"]
INGRESOS_MENSUALES = [6039.4, 9401.9, 8914.5, 9671.9, 22894.9, 19523.7, 5138.0, 3599.6, 2104.6, 537.0, 1112.3, 0.0]

CLASIF_META = {
    "Trámites realizados": {"icon": "ti-file-check", "tag_bg": VERDE_LIGHT, "tag_color": VERDE_DARK},
    "Permisos de uso de espacios públicos": {"icon": "ti-building-community", "tag_bg": GUINDA_LIGHT, "tag_color": GUINDA_DARK},
    "Permisos fúnebres diversos": {"icon": "ti-flower", "tag_bg": "#EDEAE3", "tag_color": INK_SOFT},
}


def _dinero(v):
    return f"${v:,.2f}"


# ==========================================================
# BLOQUES DE LAYOUT
# ==========================================================

def _fuentes_e_iconos():
    """Google Fonts + Tabler Icons, igual que el <head> del HTML."""
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
    ], style={"display": "flex", "alignItems": "center", "gap": "9px", "marginBottom": "16px"})


def _hub_card(icono, eyebrow, valor, sub, pct_texto, status_icono, status_texto):
    return html.Div([
        html.Div([
            html.Div(
                html.Div(html.I(className=f"ti {icono}"), style={
                    "width": "100%", "height": "100%", "borderRadius": "50%", "background": VERDE_LIGHT,
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "fontSize": "24px", "color": VERDE_DARK, "border": "1px solid #fff"
                }),
                style={
                    "width": "62px", "height": "62px", "borderRadius": "50%", "flexShrink": "0", "padding": "3px",
                    "background": f"conic-gradient({VERDE} 100%, {LINE} 0)"
                }
            ),
            html.Div([
                html.Div(eyebrow, style={
                    "fontSize": "9.5px", "fontWeight": "700", "letterSpacing": ".08em",
                    "color": INK_FAINT, "textTransform": "uppercase", "marginBottom": "3px"
                }),
                html.Div(valor, style={"fontWeight": "700", "fontSize": "22px", "lineHeight": "1.2", "color": INK}),
                html.Div(sub, style={"fontSize": "11.5px", "color": INK_SOFT, "marginTop": "4px"}),
            ], style={"flex": "1", "minWidth": "0"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "16px"}),
        html.Div([
            html.Span(pct_texto, style={"fontSize": "11px", "fontWeight": "700", "color": VERDE_DARK}),
            html.Span([html.I(className=f"ti {status_icono}", style={"fontSize": "12px"}), " " + status_texto],
                       style={"fontSize": "10px", "fontWeight": "600", "letterSpacing": ".03em", "color": INK_FAINT,
                              "display": "flex", "alignItems": "center", "gap": "4px"}),
        ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                   "marginTop": "16px", "paddingTop": "14px", "borderTop": f"1px solid {LINE}"}),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px", "position": "relative",
        "padding": "24px 24px 20px", "boxShadow": "0 1px 2px rgba(84,19,42,.05)",
        "borderTop": f"3px solid {VERDE}", "width": "340px"
    })


def _area_row(nombre, cantidad, pct, recaudacion, icono):
    return html.Div([
        html.Div(html.I(className=f"ti {icono}"), style={
            "width": "30px", "height": "30px", "flexShrink": "0", "borderRadius": "50%",
            "background": VERDE_LIGHT, "color": VERDE_DARK, "display": "flex",
            "alignItems": "center", "justifyContent": "center", "fontSize": "14px"
        }),
        html.Div([
            html.Div(nombre, style={"fontSize": "12px", "fontWeight": "600", "color": INK}),
            html.Div(f"{_dinero(recaudacion)} recaudados", style={"fontSize": "10.5px", "color": INK_FAINT, "marginTop": "1px"}),
        ], style={"flex": "1", "minWidth": "0"}),
        html.Div([
            html.Div(f"{cantidad:g}", style={"fontSize": "13px", "fontWeight": "700", "color": GUINDA_DARK}),
            html.Div(f"{pct:.1f}%", style={"fontSize": "10px", "color": INK_FAINT}),
        ], style={"textAlign": "right", "flexShrink": "0"}),
    ], style={"display": "flex", "alignItems": "center", "gap": "11px", "padding": "9px 8px",
              "borderRadius": "6px", "borderBottom": f"1px solid #F2EFE9"})


def _tag(texto, bg, color):
    return html.Span(texto, style={
        "display": "inline-block", "fontSize": "10px", "fontWeight": "600",
        "padding": "3px 9px", "borderRadius": "20px", "background": bg, "color": color
    })


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================

def analizar_licencias_reglamentos(df=None):
    """
    Módulo operativo — 3.2 Licencias y Reglamentos.
    Réplica exacta del dashboard HTML de referencia, con datos planos.
    """
    total_tramites = sum(a["cantidad"] for a in ACTIVIDADES)
    total_recaudado = sum(a["recaudacion"] for a in ACTIVIDADES)

    # ---- clasificaciones agregadas ----
    clasificaciones = {}
    for a in ACTIVIDADES:
        c = clasificaciones.setdefault(a["clasificacion"], {"cantidad": 0, "recaudacion": 0.0})
        c["cantidad"] += a["cantidad"]
        c["recaudacion"] += a["recaudacion"]

    # ---- tarjetas hub ----
    hub_row = html.Div([
        _hub_card("ti-coin", "Periodo SEP – AGO", _dinero(total_recaudado), "Total recaudado por el área",
                   "Recaudación", "ti-cash", "Acumulado del periodo"),
        _hub_card("ti-list-check", "Periodo SEP – AGO", f"{total_tramites}", "Trámites realizados",
                   "Trámites", "ti-clipboard-list", f"{len(ACTIVIDADES)} actividades"),
    ], style={"display": "flex", "justifyContent": "center", "gap": "24px", "marginBottom": "28px", "flexWrap": "wrap"})

    # ---- gráfico de pastel (Plotly, mismos colores que Chart.js) ----
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(clasificaciones.keys()),
        values=[c["cantidad"] for c in clasificaciones.values()],
        marker=dict(colors=[GUINDA, VERDE, "#C9A0AE"], line=dict(color="#fff", width=2)),
        hovertemplate="%{label}: %{value} trámites (%{percent})<extra></extra>",
        textinfo="none",
    )])
    fig_pie.update_layout(
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15, font=dict(family="Inter", size=11)),
        margin=dict(l=10, r=10, t=10, b=10), height=280, autosize=True, paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color=INK)
    )
    pie_card = html.Div(
        dcc.Graph(figure=fig_pie, config={"displayModeBar": False, "responsive": True},
                   style={"width": "100%", "maxWidth": "320px"}),
        style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {GUINDA}", "padding": "24px", "display": "flex",
               "flexDirection": "column", "alignItems": "center", "overflow": "hidden",
               "boxSizing": "border-box", "width": "100%"}
    )

    # ---- panel de clasificación ----
    areas_list = [
        _area_row(nombre, c["cantidad"], c["cantidad"] / total_tramites * 100, c["recaudacion"],
                  CLASIF_META.get(nombre, {}).get("icon", "ti-tag"))
        for nombre, c in clasificaciones.items()
    ]
    areas_panel = html.Div([
        html.Div([
            html.I(className="ti ti-folder", style={"fontSize": "16px", "color": "#EBC9D3"}),
            html.Div([
                html.Div("Resumen por clasificación", style={"fontWeight": "700", "fontSize": "12.5px", "color": "#fff"}),
                html.Div("Trámites, participación % y recaudación", style={"fontSize": "10.5px", "color": "#D9A9B7", "marginTop": "1px"}),
            ]),
        ], style={"background": GUINDA_DARK, "display": "flex", "alignItems": "center", "gap": "10px", "padding": "13px 17px"}),
        html.Div(areas_list, style={"padding": "6px 8px"}),
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px", "overflow": "hidden"})

    pastel_row = dbc.Row([
        dbc.Col(pie_card, md=5, className="mb-3"),
        dbc.Col(areas_panel, md=7, className="mb-3"),
    ])

    # ---- gráficas financieras ----
    fig_line = go.Figure(data=[go.Scatter(
        x=MESES, y=INGRESOS_MENSUALES, mode="lines+markers",
        line=dict(color=GUINDA), marker=dict(color=GUINDA),
    )])
    fig_line.update_layout(
        margin=dict(l=50, r=15, t=10, b=15), plot_bgcolor="white", paper_bgcolor="white", height=280,
        yaxis=dict(gridcolor="#f0f0f0", tickprefix="$", tickfont=dict(color=INK_SOFT)),
        xaxis=dict(tickfont=dict(color=INK_SOFT)),
        font=dict(family="Inter, sans-serif")
    )

    def _chart_panel(titulo, fig):
        return html.Div([
            html.Div(titulo, style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
                                     "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"}),
            dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True}, style={"width": "100%"}),
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
                   "borderTop": f"3px solid {GUINDA}", "padding": "16px 18px 8px"})

    graficas_row = dbc.Row([
        dbc.Col(_chart_panel("Comportamiento mensual de ingresos", fig_line), md=12, className="mb-3"),
    ])

    # ---- tabla de detalle ----
    header = html.Tr([
        html.Th(t, style={"background": BG, "color": INK_SOFT, "fontWeight": "700", "fontSize": "10.5px",
                           "letterSpacing": ".04em", "textTransform": "uppercase", "padding": "10px 14px",
                           "textAlign": "left", "borderBottom": f"1px solid {LINE}"})
        for t in ["Actividad", "Clasificación", "Cantidad", "Recaudación"]
    ])
    filas = []
    for a in ACTIVIDADES:
        meta = CLASIF_META.get(a["clasificacion"], {"tag_bg": "#EDEAE3", "tag_color": INK_SOFT})
        filas.append(html.Tr([
            html.Td(a["actividad"], style={"padding": "10px 14px", "fontSize": "12.5px", "borderBottom": f"1px solid {LINE}"}),
            html.Td(_tag(a["clasificacion"], meta["tag_bg"], meta["tag_color"]),
                    style={"padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}),
            html.Td(f"{a['cantidad']}", style={"padding": "10px 14px", "fontSize": "12.5px", "fontWeight": "600", "borderBottom": f"1px solid {LINE}"}),
            html.Td(_dinero(a["recaudacion"]), style={"padding": "10px 14px", "fontSize": "12.5px", "fontWeight": "600", "borderBottom": f"1px solid {LINE}"}),
        ]))

    tabla_detalle = html.Div(
        html.Table([html.Thead(header), html.Tbody(filas)], style={"borderCollapse": "collapse", "width": "100%"}),
        style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {VERDE}", "overflow": "hidden"}
    )

    foot_note = html.Div([
        html.I(className="ti ti-info-circle", style={"fontSize": "13px"}),
        html.Span("Datos consolidados del periodo SEP–AGO para el área 3.2 Licencias y Reglamentos."),
    ], style={"display": "flex", "alignItems": "center", "gap": "6px", "fontSize": "11px", "color": INK_FAINT, "marginTop": "20px"})

    # ---- layout final ----
    return html.Div([
        _fuentes_e_iconos(),
        hub_row,
        _section_label("ti-chart-pie", "Distribución por clasificación"),
        pastel_row,
        _section_label("ti-chart-bar", "Análisis financiero"),
        graficas_row,
        _section_label("ti-table", "Detalle por actividad"),
        tabla_detalle,
        foot_note,
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "22px 24px 54px"})