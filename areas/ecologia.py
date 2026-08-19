# areas/ecologia.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, callback

# ==========================================================
# PALETA INSTITUCIONAL
# ==========================================================
GUINDA, GUINDA_DARK, GUINDA_LIGHT = "#781D37", "#54132A", "#F3E7EB"
VERDE, VERDE_DARK, VERDE_LIGHT = "#1CA2A9", "#147880", "#E3F5F6"
BG, CARD, INK, INK_SOFT, INK_FAINT, LINE = "#EFEDE6", "#FFFFFF", "#241E1B", "#6B625C", "#9B928C", "#E3DDD2"
FONT_SANS = "'Inter', sans-serif"
FONT_SERIF = "'Playfair Display', serif"

COLORES_SERIES = [GUINDA, VERDE, "#BC955C", GUINDA_DARK, VERDE_DARK, INK_SOFT, "#2563eb"]

# ==========================================================
# COMPONENTES DE LAYOUT
# ==========================================================
def _fuentes_e_iconos():
    return html.Div([
        html.Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;700&display=swap"),
        html.Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css"),
    ])

def _section_label(icono, texto):
    return html.Div([
        html.I(className=f"ti {icono}", style={"color": VERDE, "fontSize": "16px"}),
        html.Span(texto, style={
            "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "14px", "letterSpacing": ".04em", 
            "color": GUINDA_DARK, "textTransform": "uppercase"
        }),
        html.Div(style={"flex": "1", "height": "1px", "background": LINE}),
    ], style={"display": "flex", "alignItems": "center", "gap": "9px", "margin": "22px 0 16px"})

def _kpi_card(icono, eyebrow, valor, sub, color=VERDE):
    color_light = VERDE_LIGHT if color == VERDE else GUINDA_LIGHT
    color_dark = VERDE_DARK if color == VERDE else GUINDA_DARK
    return html.Div([
        html.Div([
            html.Div(html.I(className=f"ti {icono}"), style={
                "width": "50px", "height": "50px", "borderRadius": "50%", "background": color_light,
                "display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "20px", "color": color_dark
            }),
            html.Div([
                html.Div(eyebrow, style={"fontSize": "9.5px", "fontWeight": "700", "textTransform": "uppercase", "color": INK_FAINT}),
                html.Div(valor, style={"fontWeight": "700", "fontSize": "15px", "color": INK}),
                html.Div(sub, style={"fontSize": "10.5px", "color": INK_SOFT}),
            ], style={"flex": "1", "minWidth": "0"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "14px"}),
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px", "padding": "18px", "borderTop": f"3px solid {color}"})

def _panel_header(icono, texto, color=VERDE_DARK):
    return html.Div([
        html.I(className=f"ti {icono}", style={"fontSize": "14px", "marginRight": "8px"}),
        html.Span(texto),
    ], style={
        "backgroundColor": color, "color": "#fff", "padding": "10px 14px",
        "fontWeight": "700", "fontSize": "11px", "textTransform": "uppercase", "borderRadius": "8px 8px 0 0"
    })

def _chart_panel(header_icono, header_texto, header_color, subtitulo, graph_element):
    return html.Div([
        _panel_header(header_icono, header_texto, header_color),
        html.Div([
            html.P(subtitulo, style={"fontSize": "11px", "color": INK_SOFT, "fontWeight": "500", "textAlign": "center", "marginBottom": "6px"}),
            graph_element,
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderTop": "0", "borderRadius": "0 0 8px 8px", "padding": "12px"}),
    ], style={"boxShadow": "0 1px 3px rgba(84,19,42,.06)", "marginBottom": "15px"})

# ==========================================================
# TABLA INTERACTIVA
# ==========================================================
ID_DROPDOWN_ECO = "eco-dropdown"
ID_TABLA_ECO = "eco-tabla"
_cache_eco = {"data": pd.DataFrame()}

def _tabla_detalle(df_detalle, columnas_mostrar, etiquetas):
    opciones = sorted(df_detalle["ACTIVIDAD"].dropna().unique().tolist())
    selector = html.Div([
        html.Div([
            html.I(className="ti ti-search", style={"color": VERDE, "fontSize": "14px", "marginRight": "6px"}),
            html.Span("CONSULTA DE ACTIVIDADES Y ACCIONES", style={"fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "12px", "color": GUINDA_DARK, "textTransform": "uppercase"}),
        ], style={"marginBottom": "8px"}),
        dcc.Dropdown(
            id=ID_DROPDOWN_ECO, 
            options=[{"label": str(c).title(), "value": c} for c in opciones],
            placeholder="Selecciona o busca una actividad específica...", 
            clearable=True, 
            style={"fontFamily": FONT_SANS, "fontSize": "12px"}
        )
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px", "borderTop": f"3px solid {VERDE}", "padding": "16px", "marginBottom": "14px"})

    tabla = dash_table.DataTable(
        id=ID_TABLA_ECO, 
        columns=[{"name": etiquetas.get(c, c), "id": c} for c in columnas_mostrar],
        data=df_detalle[columnas_mostrar].to_dict("records"),
        sort_action="native", page_action="native", page_size=8,
        style_header={"backgroundColor": GUINDA_DARK, "color": "#fff", "fontSize": "11px", "textTransform": "uppercase", "padding": "10px"},
        style_cell={"textAlign": "left", "padding": "10px", "fontSize": "12px", "borderBottom": f"1px solid {LINE}"},
        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"}]
    )
    return html.Div([selector, html.Div(tabla, style={"background": CARD, "borderRadius": "8px", "overflow": "hidden"})])

@callback(Output(ID_TABLA_ECO, "data"), Input(ID_DROPDOWN_ECO, "value"))
def _actualizar_tabla(actividad):
    df = _cache_eco["data"]
    if df.empty: return []
    if actividad: df = df[df["ACTIVIDAD"] == actividad]
    return df.to_dict("records")

# ==========================================================
# MÓDULO PRINCIPAL DE ANÁLISIS
# ==========================================================
def analizar_ecologia(df):
    if df is None or df.empty: 
        return dbc.Alert("⚠️ Datos vacíos en Ecología", color="warning")

    df = df.copy()
    df.columns = [str(c).upper().strip() for c in df.columns]
    
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0)
    df["VARIABLE"] = df["VARIABLE"].astype(str).str.strip()
    df["ACTIVIDAD"] = df["ACTIVIDAD"].astype(str).str.strip()
    df["MES"] = df["MES"].astype(str).str.strip()

    # --- GRÁFICA 1: Inversión por tipo de actividad ---
    df_inversion = df[df["ACTIVIDAD"].str.contains("INVERSIÓN", case=False, na=False) & ~df["ACTIVIDAD"].isin(["INVERSIÓN TOTAL"])]
    if df_inversion.empty:
        df_inversion = df.groupby("VARIABLE")["CANTIDAD"].sum().reset_index()
    
    fig_inv = px.bar(df_inversion, x="CANTIDAD", y="ACTIVIDAD", orientation="h", color_discrete_sequence=[GUINDA])
    fig_inv.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=260, margin=dict(l=10, r=10, t=10, b=10))

    # --- GRÁFICA 2: Acciones de Control Animal y Reforestación ---
    acciones_interes = ["CANINOS VACUNADOS", "FELINOS VACUNADOS", "ÁRBOLES DONADOS", "ADOPCIONES REALIZADAS", "DENUNCIAS REALIZADAS EN PROTECCIÓN ANIMAL"]
    df_social = df[df["ACTIVIDAD"].isin(acciones_interes)]
    fig_social = px.bar(df_social, x="ACTIVIDAD", y="CANTIDAD", color="ACTIVIDAD", color_discrete_sequence=COLORES_SERIES)
    fig_social.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=260, showlegend=False, margin=dict(l=10, r=10, t=10, b=40))
    fig_social.update_xaxes(tickangle=-25, tickfont=dict(size=9))

    # --- CACHÉ Y TABLA ---
    _cache_eco["data"] = df
    panel_tabla = _tabla_detalle(df, ["MES", "ACTIVIDAD", "VARIABLE", "CANTIDAD"], 
                                {"MES": "Mes", "ACTIVIDAD": "Actividad", "VARIABLE": "Variable", "CANTIDAD": "Cantidad / Monto"})

    return html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-leaf", "Indicadores Estratégicos para Informe de Gobierno"),
        # TARJETAS CON VALORES PLANOS Y CONSOLIDADOS INSTITUCIONALMENTE
        dbc.Row([
            dbc.Col(_kpi_card("ti-cash", "Inversión Total", "$1,480,033.93", "Inversión total aplicada a la operación general del area, (Recolección de Residuos,Reciclaje,Esterilizaciónes, etc.)", GUINDA), md=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-recycle", "Limpias y Reciclaje", "575,034.31 un.", "Eje operativo y descacharrización", VERDE), md=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-paw", "Control Animal y Salud", "202,867.09 un.", "Vacunaciones y esterilizaciones", GUINDA), md=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-chart-pie", "Impacto General Consolidado", "2,447,939 un.", "Total de unidades e indicadores", VERDE), md=3, className="mb-3"),
        ]),
        _section_label("ti-chart-bar", "Desglose Analítico de Gestión"),
        dbc.Row([
            dbc.Col(_chart_panel("ti-coin", "Distribución de Inversión", GUINDA_DARK, "Asignación de recursos por rubro operativo.", dcc.Graph(figure=fig_inv, config={"displayModeBar": False})), md=6),
            dbc.Col(_chart_panel("ti-paw", "Impacto Social y Ambiental Directo", VERDE_DARK, "Resultado en salud animal y reforestación.", dcc.Graph(figure=fig_social, config={"displayModeBar": False})), md=6),
        ]),
        _section_label("ti-table", "Padrón Detallado de Actividades"),
        panel_tabla
    ], style={"padding": "10px", "background": BG})