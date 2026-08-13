# areas/estado_familiar.py
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
# BLOQUES DE LAYOUT (idénticos a los usados en bibliotecas.py)
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


def _chart_panel(titulo, fig, color_top=GUINDA):
    return html.Div([
        html.Div(titulo, style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
                                 "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"}),
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True}, style={"width": "100%"}),
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {color_top}", "padding": "16px 18px 8px", "overflow": "hidden"})


def analizar_estado_familiar(df):
    """
    Módulo operativo para el Registro del Estado Familiar.
    - Cuadrícula compacta de KPIs en 2x2 con indicadores clave.
    - Tabla consolidada con scroll vertical y orden por volumen.
    - Gráfica de líneas con marcadores para seguimiento mensual de trámites.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Registro del Estado Familiar llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # LISTA DE ORDEN DE MESES GLOBAL
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # 1. Copiar y limpiar nombres de columnas
        df_ef = df.copy()
        df_ef.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_ef.columns]

        col_actividad = next((c for c in df_ef.columns if "ACTIVIDAD" in c), None)
        col_atendidos = next((c for c in df_ef.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_mes = next((c for c in df_ef.columns if "MES" in c), None)

        # 2. Conversión limpia de tipos de datos
        if col_atendidos:
            df_ef[col_atendidos] = pd.to_numeric(df_ef[col_atendidos], errors='coerce').fillna(0)
            col_cantidad_sistema = col_atendidos
        else:
            df_ef["CANTIDAD_GENERICA"] = 0
            col_cantidad_sistema = "CANTIDAD_GENERICA"

        if col_actividad: df_ef[col_actividad] = df_ef[col_actividad].astype(str).str.strip().str.title()
        if col_mes: df_ef[col_mes] = df_ef[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. CÓMPUTO DE REGLAS DE NEGOCIO (KPIs)
        # =================================================================
        total_nacimientos = df_ef[df_ef[col_actividad].str.contains("nacimiento", case=False, na=False)][col_cantidad_sistema].sum()
        total_asesorias = df_ef[df_ef[col_actividad].str.contains("asesoria|aseroria", case=False, na=False)][col_cantidad_sistema].sum()

        # Actos solemnes y civiles (matrimonios, defunciones, divorcios)
        total_civiles = df_ef[df_ef[col_actividad].str.contains("matrimonio|defuncion|divorcio", case=False, na=False)][col_cantidad_sistema].sum()

        total_atenciones = df_ef[col_cantidad_sistema].sum()

        # =================================================================
        # 4. TARJETAS KPI (estilo institucional: badge-ring + borde superior)
        # =================================================================
        kpis_row = dbc.Row([
            dbc.Col(_kpi_card("ti-file-certificate", "Actas y registros de nacimiento", f"{int(total_nacimientos):,} trámites", "Certeza jurídica inicial", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-scale", "Asesorías jurídicas registrales", f"{int(total_asesorias):,} atenciones", "Orientación a la ciudadanía", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-heart", "Actos civiles (matrimonios/defunciones)", f"{int(total_civiles):,} registros", "Eventos vitales del municipio", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-bolt", "Total general de atenciones", f"{int(total_atenciones):,} acciones", "Impacto operativo del periodo", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
        ])

        # =================================================================
        # 5. TABLA DE DETALLE (estilo institucional: header guinda, borde superior verde)
        # =================================================================
        df_resumen = df_ef.groupby([col_actividad])[col_cantidad_sistema].sum().reset_index()
        df_resumen = df_resumen[df_resumen[col_cantidad_sistema] > 0]
        df_resumen = df_resumen.sort_values(by=col_cantidad_sistema, ascending=False)

        th_style = {"fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
                    "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
                    "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}"}
        td_style = {"fontSize": "12.5px", "color": INK, "padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}

        filas_tabla = []
        for i, (_, r) in enumerate(df_resumen.iterrows()):
            bg = "#FAF8F4" if i % 2 == 1 else CARD
            filas_tabla.append(html.Tr([
                html.Td(r[col_actividad], style={**td_style, "backgroundColor": bg, "fontWeight": "600"}),
                html.Td("Dirección del Estado Familiar", style={**td_style, "backgroundColor": bg}),
                html.Td(f"{r[col_cantidad_sistema]:,.0f}", style={**td_style, "backgroundColor": bg, "textAlign": "center", "fontWeight": "700", "color": GUINDA_DARK}),
            ]))

        fila_total = html.Tr([
            html.Td("TOTAL GENERAL DE TÉRMINOS Y TRÁMITES REGISTRALES", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
            html.Td("Consolidado Anual del Área", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
            html.Td(f"{int(total_atenciones):,}", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": GUINDA, "textAlign": "center"}),
        ])

        th_sticky = {**th_style, "position": "sticky", "top": "0", "zIndex": "1"}

        tabla_layout = html.Div([
            # Encabezado fijo
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Trámite / Actividad Registrada", style={**th_sticky, "width": "50%"}),
                    html.Th("Área de Adscripción", style={**th_sticky, "width": "35%"}),
                    html.Th("Total Absoluto", style={**th_sticky, "textAlign": "center", "width": "15%", "backgroundColor": GUINDA}),
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
        ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
                  "borderTop": f"3px solid {VERDE}", "overflow": "hidden"})

        # =================================================================
        # 6. GRÁFICA INFERIOR: LÍNEAS CON MARCADORES (TENDENCIA MENSUAL)
        # =================================================================
        if col_mes:
            df_tendencia = df_ef.groupby([col_mes])[col_cantidad_sistema].sum().reset_index()
            df_tendencia[col_mes] = pd.Categorical(df_tendencia[col_mes], categories=orden_meses, ordered=True)
            df_tendencia = df_tendencia.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_tendencia = pd.DataFrame()

        if not df_tendencia.empty and df_tendencia[col_cantidad_sistema].sum() > 0:
            fig_tendencia = px.line(
                df_tendencia, x=col_mes, y=col_cantidad_sistema,
                markers=True,
                color_discrete_sequence=[GUINDA],
                labels={col_cantidad_sistema: "Volumen Total", col_mes: ""}
            )
            fig_tendencia.update_traces(line=dict(width=3), marker=dict(size=8))
            fig_tendencia.update_layout(
                margin=dict(l=40, r=15, t=10, b=15),
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=280,
                yaxis={'gridcolor': '#f0f0f0', 'tickfont': dict(color=INK_SOFT)},
                xaxis=dict(tickangle=0, categoryorder='array', categoryarray=orden_meses, tickfont=dict(color=INK_SOFT)),
                font=dict(family="Inter, sans-serif")
            )
            seccion_grafica = _chart_panel("Dinámica mensual de atenciones y trámites registrales", fig_tendencia, color_top=GUINDA)
        else:
            seccion_grafica = html.Div("ℹ️ No hay registros suficientes para estructurar el histórico mensual.",
                                        style={"padding": "20px", "color": INK_FAINT, "fontSize": "12px"})

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general"),
            kpis_row,
            _section_label("ti-table", "Balance anual de trámites"),
            tabla_layout,
            _section_label("ti-chart-line", "Tendencia mensual"),
            seccion_grafica,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Registro del Estado Familiar: {str(e)}", color="danger", className="m-3")