# areas/mujeres.py
import pandas as pd
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

# Secuencia de colores institucionales para series múltiples
COLORES_SERIES = [GUINDA, VERDE, GUINDA_DARK, VERDE_DARK, "#BC955C", INK_SOFT]


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
    """Encabezado de panel con ícono Tabler, reemplaza los headers de color plano del original."""
    return html.Div([
        html.I(className=f"ti {icono}", style={"fontSize": "14px", "marginRight": "8px"}),
        html.Span(texto),
    ], style={
        "backgroundColor": color, "color": "#fff", "padding": "10px 14px",
        "fontWeight": "700", "fontSize": "11px", "letterSpacing": ".04em",
        "textTransform": "uppercase", "borderRadius": "8px 8px 0 0"
    })


def analizar_instancia_mujeres(df):
    """
    Módulo analítico premium para la Instancia Municipal de las Mujeres.
    Muestra los indicadores con tarjetas idénticas en estilo, tono y contenedor a la referencia.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de la Instancia de las Mujeres no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_muj = df.copy()
    df_muj.columns = [str(c).strip().upper() for c in df_muj.columns]
    columnas_reales = df_muj.columns.tolist()

    col_num = next((c for c in columnas_reales if "NUM"  in c), "NUMERO")
    col_act = next((c for c in columnas_reales if "ACT"  in c), "ACTIVIDAD")
    col_atn = next((c for c in columnas_reales if "ATEN" in c or "ATEND" in c), "ATENDIDOS")
    col_mes = next((c for c in columnas_reales if "MES"  in c), "MES")
    col_var = next((c for c in columnas_reales if "VAR"  in c), "VARIABLE")
    col_inv = next((c for c in columnas_reales if "INV"  in c), "INVERSION")

    # --- LIMPIEZA RIGUROSA ---
    df_muj[col_atn] = pd.to_numeric(df_muj[col_atn], errors='coerce').fillna(0).astype(int)
    df_muj[col_inv] = pd.to_numeric(df_muj[col_inv], errors='coerce').fillna(0)
    df_muj[col_var] = df_muj[col_var].fillna("OTRAS ACCIONES").astype(str).str.strip().str.upper()
    df_muj[col_act] = df_muj[col_act].fillna("SIN ESPECIFICAR").astype(str).str.strip()
    df_muj[col_mes] = df_muj[col_mes].fillna("S/M").astype(str).str.strip().str.upper()

    # --- CÁLCULO DE MÉTRICAS ---
    total_registros = len(df_muj)
    total_atendidos = int(df_muj[col_atn].sum())

    df_canalizaciones = df_muj[df_muj[col_var].str.contains("CANALIZA", na=False)]
    total_canalizados = int(df_canalizaciones[col_atn].sum()) if not df_canalizaciones.empty else 0

    # ==========================================================
    # KPI CARDS — estilo institucional badge-ring + borde superior
    # ==========================================================
    tarjetas_kpi = dbc.Row([
        dbc.Col(_kpi_card("ti-calendar-event", "Total de actividades",  f"{total_registros:,}",   "Registros del periodo", VERDE),  width=12, sm=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-users",           "Personas atendidas",   f"{total_atendidos:,}",   "Beneficiarias directas", GUINDA), width=12, sm=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-arrows-right",    "Casos canalizados",    f"{total_canalizados:,}", "Derivaciones efectivas", VERDE),  width=12, sm=4, className="mb-3"),
    ], className="mb-2")

    # ==========================================================
    # PANEL DE PROGRESO POR LÍNEA DE ACCIÓN (lógica original intacta)
    # ==========================================================
    df_var_filtrado  = df_muj[~df_muj[col_var].str.contains("MUJERES BENEFICIARIAS", na=False)]
    df_var_agrupado  = df_var_filtrado.groupby(col_var).agg(
        TOTAL_VALOR=(col_atn, 'sum'),
        CANTIDAD_REGISTROS=(col_act, 'count')
    ).reset_index()
    df_var_agrupado  = df_var_agrupado.sort_values(by='TOTAL_VALOR', ascending=False)
    max_val          = df_var_agrupado['TOTAL_VALOR'].max() if not df_var_agrupado.empty else 1

    items_lineas_accion = []
    for i, row in df_var_agrupado.iterrows():
        nombre_var = str(row[col_var])
        val        = row['TOTAL_VALOR']
        num_regs   = row['CANTIDAD_REGISTROS']
        porcentaje = min(int((val / max_val) * 100), 100) if max_val > 0 else 0
        color      = COLORES_SERIES[i % len(COLORES_SERIES)]

        if   "TALLER"   in nombre_var: texto_num, texto_unidad = f"{num_regs}", "talleres" if num_regs != 1 else "taller"
        elif "INSTITUC" in nombre_var: texto_num, texto_unidad = f"{val}", "inst."
        elif "RED"      in nombre_var: texto_num, texto_unidad = f"{val}", "redes" if val != 1 else "red"
        elif "CANALIZA" in nombre_var: texto_num, texto_unidad = f"{val}", "casos" if val != 1 else "caso"
        else:                          texto_num, texto_unidad = f"{val}", "acciones"

        item = html.Div([
            html.Div([
                html.Span(nombre_var.title(), style={"display": "block", "marginBottom": "5px",
                                                     "fontSize": "11.5px", "fontWeight": "700", "color": INK}),
                html.Div(
                    html.Div(style={"width": f"{porcentaje}%", "backgroundColor": color,
                                    "height": "7px", "borderRadius": "4px"}),
                    style={"height": "7px", "borderRadius": "4px", "backgroundColor": LINE, "width": "100%"}
                ),
            ], style={"flex": "1", "paddingRight": "20px"}),
            html.Div([
                html.Span(texto_num,           style={"fontSize": "14px", "fontWeight": "800", "color": color}),
                html.Span(f" {texto_unidad}",  style={"fontSize": "10px", "fontWeight": "600", "color": INK_SOFT, "marginLeft": "3px"}),
            ], style={"minWidth": "90px", "textAlign": "right", "display": "flex",
                      "alignItems": "baseline", "justifyContent": "flex-end"}),
        ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                  "marginBottom": "12px", "paddingBottom": "10px", "borderBottom": f"1px solid {LINE}"})

        items_lineas_accion.append(item)

    panel_progreso = html.Div([
        _panel_header("ti-list-check", "Indicadores de progreso por línea de acción", VERDE_DARK),
        html.Div([
            html.P("Desglose operativo y volumétrico por programa secundario.",
                   style={"fontSize": "11px", "color": INK_SOFT, "fontWeight": "500",
                          "textAlign": "center", "marginBottom": "14px"}),
            html.Div(
                items_lineas_accion if items_lineas_accion
                else [html.P("Sin registros disponibles.", style={"textAlign": "center", "color": INK_FAINT})],
                style={"maxHeight": "240px", "overflowY": "auto", "paddingRight": "5px"}
            ),
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderTop": "0",
                  "borderRadius": "0 0 8px 8px", "padding": "14px 16px", "minHeight": "280px"}),
    ], style={"boxShadow": "0 1px 3px rgba(84,19,42,.06)"})

    # ==========================================================
    # GRÁFICA DE BARRAS — comportamiento temporal (lógica original intacta)
    # ==========================================================
    df_mes_agrupado = df_muj.groupby(col_mes)[col_atn].sum().reset_index(name='TOTAL_MES')
    meses_orden     = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                       "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    df_mes_agrupado[col_mes] = pd.Categorical(df_mes_agrupado[col_mes], categories=meses_orden, ordered=True)
    df_mes_agrupado          = df_mes_agrupado.sort_values(col_mes).dropna()

    fig_temporal = go.Figure()
    for i, row in df_mes_agrupado.iterrows():
        mes    = row[col_mes]
        val    = row['TOTAL_MES']
        color  = COLORES_SERIES[i % len(COLORES_SERIES)]
        fig_temporal.add_trace(go.Bar(x=[mes], y=[val], marker_color=color, showlegend=False, hoverinfo='x+y'))

    anotaciones_pines = []
    for i, row in df_mes_agrupado.iterrows():
        mes   = row[col_mes]
        val   = row['TOTAL_MES']
        color = COLORES_SERIES[i % len(COLORES_SERIES)]
        anotaciones_pines.append(dict(
            x=mes, y=val, text=f"<b>{val}</b>", showarrow=True,
            arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor=color,
            ax=0, ay=-30, bgcolor="white", bordercolor=color,
            borderwidth=2, borderpad=3, font=dict(size=10, color=color)
        ))

    fig_temporal.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title=None, tickfont=dict(size=10, color=INK_SOFT, family="Inter"), gridcolor=LINE),
        yaxis=dict(title=None, tickfont=dict(size=10, color=INK_SOFT, family="Inter"), gridcolor=LINE),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
        annotations=anotaciones_pines,
        font=dict(family="Inter, sans-serif")
    )

    panel_grafica = html.Div([
        _panel_header("ti-chart-bar", "Comportamiento temporal: impacto mensual de atenciones", GUINDA_DARK),
        html.Div([
            html.P("Volumen histórico de personas beneficiadas por periodo mensual.",
                   style={"fontSize": "11px", "color": INK_SOFT, "fontWeight": "500",
                          "textAlign": "center", "marginBottom": "4px"}),
            dcc.Graph(figure=fig_temporal, config={"displayModeBar": False}),
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderTop": "0",
                  "borderRadius": "0 0 8px 8px", "padding": "10px 14px", "minHeight": "280px"}),
    ], style={"boxShadow": "0 1px 3px rgba(84,19,42,.06)"})

    # ==========================================================
    # TABLA DE HISTORIAL DETALLADO — dash_table con paginación
    # ==========================================================
    df_muj["INVERSION_M"] = df_muj[col_inv].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")

    columnas_tabla = [
        {"name": "Eje Estratégico",               "id": col_var},
        {"name": "Actividad Impartida / Registro", "id": col_act},
        {"name": "Mes",                            "id": col_mes},
        {"name": "Personas Atendidas",             "id": col_atn},
        {"name": "Inversión Aplicada",             "id": "INVERSION_M"},
    ]

    panel_tabla = html.Div([
        _panel_header("ti-gender-female", "Registro operativo y metas históricas — Instancia de las Mujeres", GUINDA),
        html.Div([
            dash_table.DataTable(
                data=df_muj.to_dict('records'),
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
        _section_label("ti-heart", "Resumen general"),
        tarjetas_kpi,
        dbc.Row([
            dbc.Col(panel_progreso, md=6, className="mb-4"),
            dbc.Col(panel_grafica,  md=6, className="mb-4"),
        ]),
        _section_label("ti-table", "Registro operativo detallado"),
        panel_tabla,
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})