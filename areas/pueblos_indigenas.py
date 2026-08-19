# areas/pueblos_indigenas.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, callback

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

# Secuencia para series múltiples (anillo / barras)
COLORES_SERIES = [GUINDA, VERDE, "#BC955C", GUINDA_DARK, VERDE_DARK, INK_SOFT, "#2563eb"]


# ==========================================================
# BLOQUES DE LAYOUT (idénticos a bibliotecas.py y protección civil)
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
    color_dark  = VERDE_DARK  if color == VERDE else GUINDA_DARK
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


def _panel_header(icono, texto, color=VERDE_DARK):
    return html.Div([
        html.I(className=f"ti {icono}", style={"fontSize": "14px", "marginRight": "8px"}),
        html.Span(texto),
    ], style={
        "backgroundColor": color, "color": "#fff", "padding": "10px 14px",
        "fontWeight": "700", "fontSize": "11px", "letterSpacing": ".04em",
        "textTransform": "uppercase", "borderRadius": "8px 8px 0 0"
    })


def _chart_panel_custom(header_icono, header_texto, header_color, subtitulo, graph_element):
    """Panel con encabezado institucional y gráfica interior."""
    return html.Div([
        _panel_header(header_icono, header_texto, header_color),
        html.Div([
            html.P(subtitulo, style={"fontSize": "11px", "color": INK_SOFT, "fontWeight": "500",
                                     "textAlign": "center", "marginBottom": "4px"}),
            graph_element,
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderTop": "0",
                  "borderRadius": "0 0 8px 8px", "padding": "10px 14px", "minHeight": "280px"}),
    ], style={"boxShadow": "0 1px 3px rgba(84,19,42,.06)"})


# ==========================================================
# TABLA INTERACTIVA CON FILTRO DE COMUNIDAD (Patrón Protección Civil)
# ==========================================================
ID_DROPDOWN_COMUNIDAD_PI = "pi-comunidad-dropdown"
ID_TABLA_COMUNIDAD_PI = "pi-tabla-comunidad"

_cache_detalle_pi = {"data": pd.DataFrame()}

def _tabla_detalle_comunidad(df_detalle, columnas_mostrar, etiquetas):
    comunidades_opciones = sorted(df_detalle["COMUNIDAD"].dropna().unique().tolist()) if "COMUNIDAD" in df_detalle.columns else []

    selector = html.Div([
        html.Div([
            html.I(className="ti ti-search", style={"color": VERDE, "fontSize": "14px", "marginRight": "6px"}),
            html.Span("CONSULTA DETALLADA POR COMUNIDAD", style={
                "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "12.5px",
                "letterSpacing": ".03em", "color": GUINDA_DARK, "textTransform": "uppercase"
            }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
        html.Div("Selecciona o busca una comunidad para verificar el detalle del padrón histórico, meses y apoyos:",
                 style={"fontSize": "11px", "color": INK_SOFT, "marginBottom": "10px"}),
        dcc.Dropdown(
            id=ID_DROPDOWN_COMUNIDAD_PI,
            options=[{"label": str(c).title(), "value": c} for c in comunidades_opciones],
            placeholder="Selecciona una comunidad (muestra todas si está vacío)...",
            clearable=True,
            style={"fontSize": "12.5px", "fontFamily": FONT_SANS}
        ),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {VERDE}", "padding": "16px 18px", "marginBottom": "14px"
    })

    columnas = [{"name": etiquetas.get(c, c), "id": c} for c in columnas_mostrar]

    tabla = dash_table.DataTable(
        id=ID_TABLA_COMUNIDAD_PI,
        columns=columnas,
        data=df_detalle[columnas_mostrar].to_dict("records"),
        sort_action="native",
        page_action="native",
        page_size=8,
        style_as_list_view=True,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": GUINDA_DARK, "color": "#fff", "fontWeight": "700",
            "fontSize": "10.5px", "letterSpacing": ".04em", "textTransform": "uppercase",
            "textAlign": "left", "padding": "10px 14px", "border": "none"
        },
        style_cell={
            "fontFamily": FONT_SANS, "fontSize": "12.5px", "color": INK,
            "padding": "10px 14px", "textAlign": "left", "border": "none",
            "borderBottom": f"1px solid {LINE}"
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"},
        ],
        css=[{"selector": ".dash-spreadsheet-menu", "rule": "display:none"}],
    )

    return html.Div([
        selector,
        html.Div(tabla, style={
            "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
            "overflow": "hidden"
        }),
    ])


@callback(
    Output(ID_TABLA_COMUNIDAD_PI, "data"),
    Input(ID_DROPDOWN_COMUNIDAD_PI, "value")
)
def _actualizar_tabla_detalle_pi(comunidad_seleccionada):
    df_detalle = _cache_detalle_pi["data"]
    if df_detalle.empty:
        return []
    if comunidad_seleccionada:
        df_detalle = df_detalle[df_detalle["COMUNIDAD"] == comunidad_seleccionada]
    return df_detalle.to_dict("records")


def analizar_pueblos_indigenas(df):
    """
    Módulo analítico premium e independiente para la Dirección de Pueblos Indígenas.
    Actualizado con estilo infográfico institucional y buscador de tabla interactivo.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Pueblos Indígenas no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_ind = df.copy()
    df_ind.columns = [str(c).strip().upper() for c in df_ind.columns]
    columnas_reales = df_ind.columns.tolist()

    col_mes       = next((c for c in columnas_reales if "MES"      in c), "MES")
    col_comunidad = next((c for c in columnas_reales if "COMUNIDAD" in c or "LOC" in c), "COMUNIDAD")
    col_lengua    = next((c for c in columnas_reales if "LENGUA"    in c or "MATERNA" in c), None)
    col_benef     = next((c for c in columnas_reales if "BENEF"     in c or "ATEND" in c), "BENEFICIARIOS")
    col_prog      = next((c for c in columnas_reales if "PROG"      in c or "TIPO"  in c), "TIPO DE PROGRAMA")

    # --- LIMPIEZA RIGUROSA DE DATOS ---
    if col_benef in df_ind.columns:
        df_ind[col_benef] = pd.to_numeric(df_ind[col_benef], errors='coerce').fillna(0)
    else:
        df_ind['BENEFICIARIOS_LIMPIO'] = 1
        col_benef = 'BENEFICIARIOS_LIMPIO'

    # --- CÁLCULO DE MÉTRICAS ---
    total_beneficiarios = df_ind[col_benef].sum()
    total_expedientes   = len(df_ind)

    if col_lengua:
        comunidades_lengua = df_ind[df_ind[col_lengua].astype(str).str.upper().str.strip() == "SI"][col_comunidad].nunique()
    else:
        comunidades_lengua = df_ind[col_comunidad].nunique()

    # ==========================================================
    # KPI CARDS — 2 tarjetas ajustadas (sin inversión)
    # ==========================================================
    tarjetas_kpi = dbc.Row([
        dbc.Col(_kpi_card("ti-users",       "Población indígena beneficiada",        f"{total_beneficiarios:,.0f} habs.",      "Ciudadanos atendidos de manera directa",   VERDE),  width=12, sm=6, className="mb-3"),
        dbc.Col(_kpi_card("ti-language",    "Localidades con lengua materna",        f"{comunidades_lengua} comunidades",      "Identidad cultural y hablantes activos",   GUINDA), width=12, sm=6, className="mb-3"),
    ], className="mb-2")

    # ==========================================================
    # GRÁFICA 1: ANILLO DE PROGRAMAS
    # ==========================================================
    df_ind[col_prog] = df_ind[col_prog].fillna("POR CLASIFICAR").astype(str).str.strip()
    df_programas     = df_ind.groupby(col_prog).size().reset_index(name='CONTEO')
    df_programas     = df_programas.sort_values(by='CONTEO', ascending=False).reset_index(drop=True)

    fig_programas = go.Figure(data=[go.Pie(
        labels=df_programas[col_prog],
        values=df_programas['CONTEO'],
        hole=0.6,
        textinfo='percent',
        textposition='inside',
        insidetextfont=dict(color='white', size=11, family="Inter", weight="bold"),
        marker=dict(colors=COLORES_SERIES),
        hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )])
    fig_programas.update_layout(
        annotations=[dict(text=f"<b>{total_expedientes}</b><br>Total", x=0.5, y=0.5,
                          font_size=13, font_color=INK, showarrow=False)],
        margin=dict(l=10, r=140, t=10, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
                    font=dict(size=9, color=INK, family="Inter")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280,
        font=dict(family="Inter, sans-serif")
    )

    # ==========================================================
    # GRÁFICA 2: BARRAS HORIZONTALES POR LOCALIDAD
    # ==========================================================
    df_comunidades = (
        df_ind.groupby(col_comunidad)[col_benef].sum()
              .reset_index(name='TOTAL_BENEF')
              .sort_values(by='TOTAL_BENEF', ascending=True)
              .tail(8)
    )
    fig_comunidades = px.bar(
        df_comunidades, x='TOTAL_BENEF', y=col_comunidad, orientation='h',
        color_discrete_sequence=[VERDE],
        labels={'TOTAL_BENEF': 'Ciudadanos', col_comunidad: 'Comunidad'}
    )
    fig_comunidades.update_layout(
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis=dict(title=None, gridcolor=LINE, tickfont=dict(size=10, color=INK_SOFT, family="Inter")),
        yaxis=dict(title=None, tickfont=dict(size=10, color=INK_SOFT, family="Inter")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=280,
        font=dict(family="Inter, sans-serif")
    )

    # ==========================================================
    # TABLA DE PADRÓN INTERACTIVA CON FILTRO
    # ==========================================================
    columnas_detalle = [c for c in [col_comunidad, col_mes, col_prog, col_lengua, col_benef] if c]
    if col_comunidad and columnas_detalle:
        df_detalle = df_ind[columnas_detalle].copy()
        df_detalle = df_detalle.rename(columns={col_comunidad: "COMUNIDAD"})
        df_detalle["COMUNIDAD"] = df_detalle["COMUNIDAD"].str.title()
        df_detalle = df_detalle.sort_values(by=col_benef, ascending=False) if col_benef else df_detalle

        columnas_mostrar = ["COMUNIDAD"] + [c for c in [col_mes, col_prog, col_lengua, col_benef] if c != col_comunidad]
        etiquetas = {
            "COMUNIDAD": "Comunidad Indígena", col_mes: "Periodo / Mes",
            col_prog: "Programa o Apoyo Otorgado", col_lengua: "Hablantes Maternos",
            col_benef: "Población Atendida"
        }

        _cache_detalle_pi["data"] = df_detalle[columnas_mostrar]
        panel_tabla = _tabla_detalle_comunidad(df_detalle, columnas_mostrar, etiquetas)
    else:
        panel_tabla = html.Div()

    # ==========================================================
    # LAYOUT CONSOLIDADO FINAL
    # ==========================================================
    return html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-feather", "Resumen general"),
        tarjetas_kpi,
        _section_label("ti-chart-donut", "Visualizaciones infográficas"),
        dbc.Row([
            dbc.Col(
                _chart_panel_custom(
                    "ti-chart-pie", "Participación de programas sociales en comunidades", VERDE_DARK,
                    "Distribución porcentual de apoyos otorgados por tipo de programa.",
                    dcc.Graph(figure=fig_programas, config={"displayModeBar": False})
                ),
                md=6, className="mb-4"
            ),
            dbc.Col(
                _chart_panel_custom(
                    "ti-chart-bar", "Top localidades indígenas con mayor impacto de atención", GUINDA_DARK,
                    "Localidades con mayor volumen de población indígena beneficiada.",
                    dcc.Graph(figure=fig_comunidades, config={"displayModeBar": False})
                ),
                md=6, className="mb-4"
            ),
        ]),
        _section_label("ti-table", "Padrón histórico de atención"),
        panel_tabla,
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})