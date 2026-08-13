# areas/secretaria_general.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

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


# ==========================================================
# BLOQUES DE LAYOUT (idénticos a bibliotecas.py)
# ==========================================================

def _fuentes_e_iconos():
    """Google Fonts + Tabler Icons, misma fuente tipográfica del sistema."""
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


def _chart_panel(titulo, fig, color_top=GUINDA):
    return html.Div([
        html.Div(titulo, style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
                                 "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"}),
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True}, style={"width": "100%"}),
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {color_top}", "padding": "16px 18px 8px", "overflow": "hidden"})


def analizar_secretaria_general(df):
    """
    Módulo operativo para la Secretaría General.
    - Cuadrícula compacta de KPIs en 2x2.
    - Tabla optimizada con desplazamiento vertical (scroll), filtrado de ceros y diseño compacto.
    - Gráfica de líneas con marcadores para tendencia mensual limpia.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Secretaría General llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # LISTA DE ORDEN DE MESES GLOBAL
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # 1. Copiar y limpiar nombres de columnas
        df_sg = df.copy()
        df_sg.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_sg.columns]

        col_actividad = next((c for c in df_sg.columns if "ACTIVIDAD" in c), None)
        col_atendidos = next((c for c in df_sg.columns if "ATENDID"   in c or "CANTIDAD" in c), None)
        col_mes       = next((c for c in df_sg.columns if "MES"       in c), None)
        col_variable  = next((c for c in df_sg.columns if "VARIABLE"  in c), None)

        # 2. Conversión limpia de tipos de datos
        if col_atendidos:
            df_sg[col_atendidos] = pd.to_numeric(df_sg[col_atendidos], errors='coerce').fillna(0)
            col_cantidad_sistema = col_atendidos
        else:
            df_sg["CANTIDAD_GENERICA"] = 0
            col_cantidad_sistema = "CANTIDAD_GENERICA"

        if col_variable:  df_sg[col_variable]  = df_sg[col_variable].astype(str).str.strip().str.title()
        if col_actividad: df_sg[col_actividad] = df_sg[col_actividad].astype(str).str.strip().str.title()
        if col_mes:       df_sg[col_mes]       = df_sg[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. CÓMPUTO DE KPIs
        # =================================================================
        total_audiencias = df_sg[df_sg[col_actividad].str.contains("audiencia",           case=False, na=False)][col_cantidad_sistema].sum()
        total_documentos = df_sg[df_sg[col_actividad].str.contains("constancia|documento", case=False, na=False)][col_cantidad_sistema].sum()
        total_cabildo    = df_sg[df_sg[col_actividad].str.contains("cabildo",              case=False, na=False)][col_cantidad_sistema].sum()
        total_gestiones  = total_audiencias + total_documentos + total_cabildo

        # ==========================================================
        # 4. KPI CARDS — cuadrícula 2×2, estilo institucional
        # ==========================================================
        cuadricula_kpis = html.Div([
            dbc.Row([
                dbc.Col(_kpi_card("ti-speakerphone",  "Audiencias con la ciudadanía",       f"{int(total_audiencias):,} atendidas", "Atención directa del Secretario",      VERDE),  width=12, md=6, className="mb-3"),
                dbc.Col(_kpi_card("ti-file-text",     "Constancias y trámites",             f"{int(total_documentos):,} emitidas",  "Certeza jurídica e identidad",          GUINDA), width=12, md=6, className="mb-3"),
            ], className="g-2"),
            dbc.Row([
                dbc.Col(_kpi_card("ti-building",      "Sesiones de cabildo efectuadas",     f"{int(total_cabildo):,} sesiones",    "Ordinarias y Extraordinarias",          VERDE),  width=12, md=6, className="mb-3"),
                dbc.Col(_kpi_card("ti-bolt",          "Total gestiones administrativas",    f"{int(total_gestiones):,} acciones",  "Impacto operativo total en el área",    GUINDA), width=12, md=6, className="mb-3"),
            ], className="g-2"),
        ])

        # =================================================================
        # 5. TABLA — scroll vertical, sin ceros, fila de totales fija
        # =================================================================
        df_resumen = df_sg.groupby([col_actividad, col_variable])[col_cantidad_sistema].sum().reset_index()
        df_resumen = df_resumen[df_resumen[col_cantidad_sistema] > 0]
        df_resumen = df_resumen.sort_values(by=col_cantidad_sistema, ascending=False)

        th_style = {
            "fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
            "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
            "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}",
            "position": "sticky", "top": "0", "zIndex": "1"
        }
        td_style = {"fontSize": "12.5px", "color": INK, "padding": "9px 14px", "borderBottom": f"1px solid {LINE}"}

        filas_tabla = []
        for i, (_, r) in enumerate(df_resumen.iterrows()):
            bg = "#FAF8F4" if i % 2 == 1 else CARD
            filas_tabla.append(html.Tr([
                html.Td(r[col_actividad],                    style={**td_style, "backgroundColor": bg, "fontWeight": "600"}),
                html.Td(r[col_variable],                     style={**td_style, "backgroundColor": bg, "color": INK_SOFT}),
                html.Td(f"{r[col_cantidad_sistema]:,.0f}",   style={**td_style, "backgroundColor": bg,
                                                                     "textAlign": "center", "fontWeight": "700", "color": GUINDA_DARK}),
            ]))

        # Fila de totales fuera del scroll — siempre visible
        fila_total = html.Tr([
            html.Td("TOTAL DE ATENCIONES Y GESTIONES GENERALES", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
            html.Td("Consolidado anual del área",               style={**td_style, "fontWeight": "600", "color": "#fff", "backgroundColor": VERDE_DARK}),
            html.Td(f"{int(total_gestiones):,}",                style={**td_style, "fontWeight": "700", "color": "#fff",
                                                                        "backgroundColor": GUINDA, "textAlign": "center"}),
        ])

        # Scroll cuando supera 10 filas de datos
        max_height   = "320px" if len(df_resumen) > 10 else None
        scroll_style = {"overflowY": "auto", "maxHeight": max_height} if max_height else {}

        tabla_layout = html.Div([
            html.Div(
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Actividad Registrada",            style={**th_style, "width": "45%"}),
                        html.Th("Eje Operativo / Clasificación",   style={**th_style, "width": "40%"}),
                        html.Th("Total Absoluto",                  style={**th_style, "textAlign": "center",
                                                                           "backgroundColor": GUINDA, "width": "15%"}),
                    ])),
                    html.Tbody(
                        filas_tabla if filas_tabla
                        else [html.Tr([html.Td("Sin registros", colSpan=3,
                                               style={"textAlign": "center", "color": INK_FAINT, "padding": "16px"})])]
                    ),
                ], style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
                style=scroll_style
            ),
            html.Table([html.Tbody([fila_total])],
                       style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
        ], style={
            "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
            "borderTop": f"3px solid {VERDE}", "overflow": "hidden"
        })

        # =================================================================
        # 6. GRÁFICA — tendencia mensual, colores institucionales
        # =================================================================
        if col_mes and col_variable:
            df_barras = df_sg.groupby([col_mes, col_variable])[col_cantidad_sistema].sum().reset_index()
            df_barras[col_mes] = pd.Categorical(df_barras[col_mes], categories=orden_meses, ordered=True)
            df_barras = df_barras.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_barras = pd.DataFrame()

        if not df_barras.empty and df_barras[col_cantidad_sistema].sum() > 0:
            fig_comparativa = px.line(
                df_barras, x=col_mes, y=col_cantidad_sistema, color=col_variable,
                markers=True,
                color_discrete_map={
                    "Atención Personal A La Población":    VERDE,
                    "Documentación Expedida A La Población": VERDE_DARK,
                    "Sesiones De Cabildo":                 GUINDA,
                },
                labels={col_cantidad_sistema: "Volumen", col_mes: "", col_variable: "Clasificación"}
            )
            fig_comparativa.update_traces(line=dict(width=2.5), marker=dict(size=7))
            fig_comparativa.update_layout(
                margin=dict(l=40, r=15, t=10, b=15),
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=290,
                yaxis={"gridcolor": "#f0f0f0", "tickfont": dict(color=INK_SOFT)},
                xaxis=dict(tickangle=0, categoryorder="array", categoryarray=orden_meses,
                           tickfont=dict(color=INK_SOFT)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(family="Inter", size=10)),
                font=dict(family="Inter, sans-serif")
            )
            seccion_grafica = _chart_panel(
                "Dinámica de trabajo mensual (tendencia por eje operativo)",
                fig_comparativa,
                color_top=GUINDA
            )
        else:
            seccion_grafica = html.Div(
                "ℹ️ No hay registros suficientes para estructurar el histórico.",
                style={"padding": "20px", "color": INK_FAINT, "fontSize": "12px"}
            )

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-building-community", "Cuadro de mando — Secretaría General"),
            cuadricula_kpis,
            _section_label("ti-table", "Balance anual de indicadores"),
            tabla_layout,
            _section_label("ti-chart-line", "Tendencia mensual"),
            seccion_grafica,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Secretaría General: {str(e)}", color="danger", className="m-3")