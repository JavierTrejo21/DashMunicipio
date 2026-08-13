# areas/atencion_ciudadana.py
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

# Orden cronológico oficial para la secuencia de meses
ORDEN_MESES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]


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


def _chart_panel(titulo, contenido, color_top=GUINDA):
    return html.Div([
        html.Div(titulo, style={
            "fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
            "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"
        }),
        contenido,
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {color_top}", "padding": "16px 18px 12px", "overflow": "hidden"
    })


def analizar_atencion_ciudadana(df):
    """
    Módulo analítico para el área de Atención Ciudadana.
    Presenta distribución por áreas mediante Treemap con paleta semafórica,
    tarjetas de indicadores, gráfica temporal y tabla detallada.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Atención Ciudadana no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_atc = df.copy()
    df_atc.columns = [str(c).strip().upper() for c in df_atc.columns]
    columnas_reales = df_atc.columns.tolist()

    # Identificación flexible de columnas
    col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
    col_atn = next((c for c in columnas_reales if "ATEN" in c or "ATEND" in c), "ATENDIDOS")
    col_act = next((c for c in columnas_reales if "ACT" in c), "ACTIVIDAD")
    col_var = next((c for c in columnas_reales if "VAR" in c or "AREA" in c), "VARIABLE")

    # --- LIMPIEZA RIGUROSA ---
    df_atc[col_atn] = pd.to_numeric(df_atc[col_atn], errors='coerce').fillna(0).astype(int)
    df_atc[col_var] = df_atc[col_var].fillna("OTRAS ÁREAS").astype(str).str.strip().str.upper()
    df_atc[col_act] = df_atc[col_act].fillna("SIN ESPECIFICAR").astype(str).str.strip()
    df_atc[col_mes] = df_atc[col_mes].fillna("S/M").astype(str).str.strip().str.upper()

    # --- CÁLCULO DE MÉTRICAS ---
    total_atendidos = int(df_atc[col_atn].sum())
    df_areas = df_atc.groupby(col_var)[col_atn].sum().reset_index()
    df_areas = df_areas.sort_values(by=col_atn, ascending=False)
    area_mas_solicitada = df_areas.iloc[0][col_var] if not df_areas.empty else "N/D"

    # =================================================================
    # KPI CARDS (estilo institucional: badge-ring + borde superior)
    # =================================================================
    kpis_row = dbc.Row([
        dbc.Col(_kpi_card("ti-users", "Total de ciudadanos atendidos", f"{total_atendidos:,}", "Registros del periodo", VERDE), width=12, sm=6, className="mb-3"),
        dbc.Col(_kpi_card("ti-star", "Área de mayor afluencia", area_mas_solicitada, "Departamento con más solicitudes", GUINDA), width=12, sm=6, className="mb-3"),
    ])

    # =================================================================
    # TREEMAP (paleta semafórica institucional + animación original)
    # =================================================================
    # Animación CSS original preservada
    estilos_animacion = dcc.Markdown("""
<style>
    @keyframes fadeInSlide {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .animar-entrada {
        animation: fadeInSlide 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
</style>
""", dangerously_allow_html=True)

    fig_treemap = px.treemap(
        df_areas,
        path=[col_var],
        values=col_atn,
        color=col_atn,
        color_continuous_scale=[
            [0.0, VERDE_LIGHT],
            [0.4, VERDE],
            [1.0, GUINDA],
        ],
        custom_data=[col_atn]
    )
    fig_treemap.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,} ciudadanos",
        textposition="middle center",
        textfont=dict(size=15, family="Inter, sans-serif", color="white"),
        hovertemplate="<b>Área:</b> %{label}<br><b>Ciudadanos Atendidos:</b> %{value:,}<extra></extra>"
    )
    fig_treemap.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(
            title=dict(text="Afluencia", font=dict(size=11, family="Inter, sans-serif")),
            thickness=14, len=0.85
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        font=dict(family="Inter, sans-serif")
    )

    seccion_treemap = html.Div(
        _chart_panel(
            "Concentración y distribución de presencia ciudadana por departamento",
            html.Div([
                html.P(
                    "Análisis volumétrico dimensional basado en registros de atención y audiencias ciudadanas.",
                    style={"fontSize": "12px", "color": INK_SOFT, "textAlign": "center", "marginBottom": "8px"}
                ),
                dcc.Graph(figure=fig_treemap, config={'displayModeBar': False}),
            ]),
            color_top=GUINDA
        ),
        className="animar-entrada mb-3"
    )

    # =================================================================
    # GRÁFICA DE LÍNEA TEMPORAL MENSUAL
    # =================================================================
    fig_linea = go.Figure()
    df_meses = df_atc.groupby(col_mes)[col_atn].sum().reset_index()
    df_meses['orden'] = df_meses[col_mes].apply(lambda x: ORDEN_MESES.index(x) if x in ORDEN_MESES else 99)
    df_meses = df_meses.sort_values('orden')

    if not df_meses.empty:
        fig_linea.add_trace(go.Scatter(
            x=df_meses[col_mes],
            y=df_meses[col_atn],
            mode='lines+markers+text',
            line=dict(color=GUINDA, width=3, shape='spline'),
            marker=dict(color=VERDE, size=9, line=dict(width=2, color="white")),
            text=df_meses[col_atn].apply(lambda x: f"<b>{int(x):,}</b>"),
            textposition="top center",
            textfont=dict(size=10, color=INK_SOFT, family="Inter, sans-serif"),
            fill='tozeroy',
            fillcolor=f'rgba(120, 29, 55, 0.06)',
            hovertemplate="<b>Mes:</b> %{x}<br><b>Atendidos:</b> %{y:,} ciudadanos<extra></extra>"
        ))

    fig_linea.update_layout(
        margin=dict(l=20, r=20, t=10, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
        xaxis=dict(showgrid=False, tickfont=dict(color=INK_SOFT, size=10, family="Inter, sans-serif")),
        yaxis=dict(showgrid=True, gridcolor=LINE, showticklabels=False),
        font=dict(family="Inter, sans-serif")
    )

    seccion_linea = html.Div(
        _chart_panel(
            "Comportamiento histórico y fluctuación mensual de audiencias",
            html.Div([
                html.P(
                    "Monitoreo temporal para identificar picos estacionales de solicitudes en el municipio.",
                    style={"fontSize": "12px", "color": INK_SOFT, "textAlign": "center", "marginBottom": "8px"}
                ),
                dcc.Graph(figure=fig_linea, config={'displayModeBar': False}),
            ]),
            color_top=VERDE
        ),
        className="animar-entrada mb-3"
    )

    # =================================================================
    # TABLA DETALLADA (estilo institucional + scroll vertical)
    # =================================================================
    columnas_tabla = [
        {"name": "Mes",                  "id": col_mes},
        {"name": "Área / Dirección",     "id": col_var},
        {"name": "Actividad",            "id": col_act},
        {"name": "Ciudadanos Atendidos", "id": col_atn},
    ]

    tabla_detalle = dash_table.DataTable(
        data=df_atc.to_dict('records'),
        columns=columnas_tabla,
        page_size=8,
        style_table={'overflowX': 'auto', 'overflowY': 'auto', 'maxHeight': '320px'},
        style_header={
            'backgroundColor': GUINDA_DARK,
            'color': '#ffffff',
            'fontWeight': '700',
            'fontSize': '10.5px',
            'letterSpacing': '.04em',
            'textTransform': 'uppercase',
            'textAlign': 'left',
            'border': 'none',
            'fontFamily': 'Inter, sans-serif',
            'padding': '10px 14px',
        },
        style_cell={
            'padding': '10px 14px',
            'fontSize': '12px',
            'fontFamily': 'Inter, sans-serif',
            'color': INK,
            'textAlign': 'left',
            'borderBottom': f'1px solid {LINE}',
            'backgroundColor': CARD,
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#FAF8F4'},
        ],
    )

    seccion_tabla = html.Div(
        _chart_panel(
            "Registro detallado de atención ciudadana",
            tabla_detalle,
            color_top=GUINDA
        ),
        className="animar-entrada mb-3"
    )

    # =================================================================
    # LAYOUT CONSOLIDADO FINAL
    # =================================================================
    return html.Div([
        _fuentes_e_iconos(),
        estilos_animacion,
        _section_label("ti-chart-bar", "Resumen general"),
        kpis_row,
        _section_label("ti-layout-grid", "Distribución por departamento"),
        seccion_treemap,
        _section_label("ti-chart-line", "Tendencia mensual"),
        seccion_linea,
        _section_label("ti-table", "Registro detallado"),
        seccion_tabla,
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})