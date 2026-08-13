# areas/pueblos_indigenas.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

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
# BLOQUES DE LAYOUT (idénticos a bibliotecas.py)
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


def analizar_pueblos_indigenas(df):
    """
    Módulo analítico premium e independiente para la Dirección de Pueblos Indígenas.
    Actualizado con estilo infográfico institucional y máxima legibilidad.
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
    col_inv       = next((c for c in columnas_reales if "INV"       in c), "INVERSION")

    # --- LIMPIEZA RIGUROSA DE DATOS ---
    if col_benef in df_ind.columns:
        df_ind[col_benef] = pd.to_numeric(df_ind[col_benef], errors='coerce').fillna(0)
    else:
        df_ind['BENEFICIARIOS_LIMPIO'] = 1
        col_benef = 'BENEFICIARIOS_LIMPIO'

    if col_inv in df_ind.columns:
        df_ind[col_inv] = df_ind[col_inv].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
        df_ind[col_inv] = pd.to_numeric(df_ind[col_inv], errors='coerce').fillna(0)
    else:
        df_ind['INVERSION_LIMPIA'] = 0
        col_inv = 'INVERSION_LIMPIA'

    # --- CÁLCULO DE MÉTRICAS ---
    total_inversion     = df_ind[col_inv].sum()
    total_beneficiarios = df_ind[col_benef].sum()
    total_expedientes   = len(df_ind)

    if col_lengua:
        comunidades_lengua = df_ind[df_ind[col_lengua].astype(str).str.upper().str.strip() == "SI"][col_comunidad].nunique()
    else:
        comunidades_lengua = df_ind[col_comunidad].nunique()

    # ==========================================================
    # KPI CARDS — estilo institucional badge-ring + borde superior
    # ==========================================================
    tarjetas_kpi = dbc.Row([
        dbc.Col(_kpi_card("ti-cash",        "Inversión total asignada",              f"${total_inversion:,.2f}",               "Fondos ejecutados y apoyos económicos",    GUINDA), width=12, sm=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-users",       "Población indígena beneficiada",        f"{total_beneficiarios:,.0f} habs.",      "Ciudadanos atendidos de manera directa",   VERDE),  width=12, sm=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-language",    "Localidades con lengua materna",        f"{comunidades_lengua} comunidades",      "Identidad cultural y hablantes activos",   GUINDA), width=12, sm=4, className="mb-3"),
    ], className="mb-2")

    # ==========================================================
    # GRÁFICA 1: ANILLO DE PROGRAMAS — lógica original intacta
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
    # GRÁFICA 2: BARRAS HORIZONTALES POR LOCALIDAD — lógica original intacta
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
    # TABLA DE PADRÓN — dash_table con paginación, lógica intacta
    # ==========================================================
    df_ind["INVERSION_M"] = df_ind[col_inv].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")

    columnas_tabla = [
        {"name": "Periodo / Mes",              "id": col_mes},
        {"name": "Comunidad Indígena",         "id": col_comunidad},
        {"name": "Programa o Apoyo Otorgado",  "id": col_prog},
        {"name": "Hablantes Maternos",         "id": col_lengua if col_lengua else col_comunidad},
        {"name": "Población Atendida",         "id": col_benef},
        {"name": "Inversión Aplicada",         "id": "INVERSION_M"},
    ]

    panel_tabla = html.Div([
        _panel_header("ti-notebook", "Padrón completo y histórico de atención a comunidades indígenas", GUINDA),
        html.Div([
            dash_table.DataTable(
                data=df_ind.to_dict('records'),
                columns=columnas_tabla,
                page_size=6,
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": GUINDA_LIGHT, "color": GUINDA_DARK,
                    "fontWeight": "700", "fontSize": "11px", "textAlign": "left",
                    "borderBottom": f"2px solid {LINE}", "fontFamily": "Inter, sans-serif"
                },
                style_cell={
                    "padding": "9px 10px", "fontSize": "11.5px", "fontFamily": "Inter, sans-serif",
                    "textAlign": "left", "borderBottom": f"1px solid {LINE}",
                    "color": INK, "backgroundColor": CARD
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"}
                ]
            )
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderTop": "0",
                  "borderRadius": "0 0 8px 8px", "padding": "10px"}),
    ], style={"boxShadow": "0 1px 3px rgba(84,19,42,.06)"})

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