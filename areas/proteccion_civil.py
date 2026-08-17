# areas/proteccion_civil.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, callback

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA (misma que bibliotecas.py / licencias_reglamentos.py)
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


def _chart_panel(titulo, contenido, color_top=GUINDA):
    return html.Div([
        html.Div(titulo, style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
                                 "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"}),
        contenido,
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {color_top}", "padding": "16px 18px 8px", "overflow": "hidden"})


# ==========================================================
# TABLA INTERACTIVA "DETALLE POR COMUNIDAD"
# (mismo patrón visual: header guinda, orden nativo, paginación,
#  y selector de comunidad con dropdown institucional)
# ==========================================================
ID_DROPDOWN_COMUNIDAD_PC = "pc-comunidad-dropdown"
ID_TABLA_COMUNIDAD_PC = "pc-tabla-comunidad"

# Caché simple en memoria para que el callback del dropdown pueda
# releer el último dataset procesado por analizar_proteccion_civil().
_cache_detalle_pc = {"data": pd.DataFrame()}


def _tabla_detalle_comunidad(df_detalle, columnas_mostrar, etiquetas):
    """Construye la tabla estilo institucional (header guinda, orden nativo, paginación)."""
    columnas = [{"name": etiquetas.get(c, c), "id": c} for c in columnas_mostrar]

    comunidades_opciones = sorted(df_detalle["COMUNIDAD"].dropna().unique().tolist()) if "COMUNIDAD" in df_detalle.columns else []

    selector = html.Div([
        html.Div([
            html.I(className="ti ti-search", style={"color": VERDE, "fontSize": "14px", "marginRight": "6px"}),
            html.Span("CONSULTA DETALLADA POR COMUNIDAD", style={
                "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "12.5px",
                "letterSpacing": ".03em", "color": GUINDA_DARK, "textTransform": "uppercase"
            }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
        html.Div("Selecciona o busca una comunidad para verificar el detalle de emergencias, meses y actividades:",
                 style={"fontSize": "11px", "color": INK_SOFT, "marginBottom": "10px"}),
        dcc.Dropdown(
            id=ID_DROPDOWN_COMUNIDAD_PC,
            options=[{"label": c.title(), "value": c} for c in comunidades_opciones],
            placeholder="Selecciona una comunidad (muestra todas si está vacío)...",
            clearable=True,
            style={"fontSize": "12.5px", "fontFamily": FONT_SANS}
        ),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {VERDE}", "padding": "16px 18px", "marginBottom": "14px"
    })

    tabla = dash_table.DataTable(
        id=ID_TABLA_COMUNIDAD_PC,
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
    Output(ID_TABLA_COMUNIDAD_PC, "data"),
    Input(ID_DROPDOWN_COMUNIDAD_PC, "value")
)
def _actualizar_tabla_detalle_pc(comunidad_seleccionada):
    df_detalle = _cache_detalle_pc["data"]
    if df_detalle.empty:
        return []
    if comunidad_seleccionada:
        df_detalle = df_detalle[df_detalle["COMUNIDAD"] == comunidad_seleccionada]
    return df_detalle.to_dict("records")


def analizar_proteccion_civil(df):
    """
    Módulo operativo para Protección Civil.
    Analiza el flujo de emergencias, riesgos meteorológicos e impacto por comunidades.
    Misma estructura visual y colorimetría institucional (guinda/verde) que
    el módulo de Bibliotecas y C.C.A.; la lógica analítica no cambia.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Protección Civil llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_pc = df.copy()
        df_pc.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_pc.columns]

        # Identificación dinámica de columnas
        col_mes = next((c for c in df_pc.columns if "MES" in c), None)
        col_atendidos = next((c for c in df_pc.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_pc.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_pc.columns if "VARIABLE" in c), None)
        col_comunidad = next((c for c in df_pc.columns if "COMUNIDAD" in c or "LOCALIDAD" in c), None)

        # 2. Conversión limpia de datos y estandarización
        if col_atendidos:
            df_pc[col_atendidos] = pd.to_numeric(df_pc[col_atendidos], errors='coerce').fillna(0)
            # Homologación global del sistema por si algún callback externo busca 'CANTIDAD'
            df_pc["CANTIDAD"] = df_pc[col_atendidos]
            col_cantidad_sistema = "CANTIDAD"
        else:
            df_pc["CANTIDAD"] = 0
            col_cantidad_sistema = "CANTIDAD"

        if col_variable: df_pc[col_variable] = df_pc[col_variable].astype(str).str.strip()
        if col_actividad:
            df_pc[col_actividad] = df_pc[col_actividad].astype(str).str.strip()
            # Normalización de variantes ortográficas para no duplicar categorías (p.ej. "Inudaciónes" -> "Inundaciones")
            df_pc[col_actividad] = df_pc[col_actividad].replace({
                "Inudaciónes": "Inundaciones", "Inudaciones": "Inundaciones", "Inundaciónes": "Inundaciones"
            })
        if col_comunidad: df_pc[col_comunidad] = df_pc[col_comunidad].astype(str).str.strip().str.upper()
        if col_mes: df_pc[col_mes] = df_pc[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. EXTRACCIÓN DE MÉTRICAS OPERATIVAS (FILTROS EXCLUSIVOS)
        # =================================================================
        total_emergencias = df_pc[col_cantidad_sistema].sum()

        # 'meteor|clima|riesgo' atrapa "Atención a Riesgos Meteorológicos"
        df_meteorologicos = df_pc[df_pc[col_variable].str.contains("meteor|clima|riesgo", case=False, na=False)] if col_variable else pd.DataFrame()
        total_meteorologicos = df_meteorologicos[col_cantidad_sistema].sum() if not df_meteorologicos.empty else 0

        # SOLUCIÓN DE DUPLICIDAD: Al buscar solo por 'poblac' aislamos "Atención a la Población" de forma única
        df_poblacion = df_pc[df_pc[col_variable].str.contains("poblac", case=False, na=False)] if col_variable else pd.DataFrame()
        total_poblacion = df_poblacion[col_cantidad_sistema].sum() if not df_poblacion.empty else 0

        # Obtener la comunidad con mayor incidencia
        if col_comunidad and not df_pc.empty:
            df_top_com = df_pc.groupby(col_comunidad)[col_cantidad_sistema].sum().reset_index()
            # Filtrar posibles registros vacíos o guiones de formato
            df_top_com = df_top_com[~df_top_com[col_comunidad].str.contains("UNKNOWN|VACIO|-|S/N", na=False)]
            if not df_top_com.empty and df_top_com[col_cantidad_sistema].sum() > 0:
                top_com_row = df_top_com.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0]
                top_comunidad_nombre = str(top_com_row[col_comunidad]).title()
                if len(top_comunidad_nombre) > 22: top_comunidad_nombre = top_comunidad_nombre[:19] + "..."
            else:
                top_comunidad_nombre = "Sin registros"
        else:
            top_comunidad_nombre = "No disponible"

        # Cobertura territorial: nº de comunidades distintas atendidas y % de atenciones fuera de la cabecera
        if col_comunidad and not df_pc.empty:
            comunidades_atendidas = df_pc[df_pc[col_cantidad_sistema] > 0][col_comunidad].nunique()
            atenciones_cabecera = df_pc[df_pc[col_comunidad].str.contains("CABECERA", case=False, na=False)][col_cantidad_sistema].sum()
            pct_cobertura_rural = ((total_emergencias - atenciones_cabecera) / total_emergencias * 100) if total_emergencias > 0 else 0
        else:
            comunidades_atendidas = 0
            pct_cobertura_rural = 0

        # =================================================================
        # 4. TARJETAS KPI (estilo institucional: badge-ring + borde superior)
        # =================================================================
        kpis_row = dbc.Row([
            dbc.Col(_kpi_card("ti-alert-triangle", "Emergencias atendidas", f"{total_emergencias:,.0f} servicios", "Total de auxilios en el municipio", GUINDA), width=12, sm=6, lg=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-cloud-storm", "Riesgos meteorológicos", f"{total_meteorologicos:,.0f} eventos", "Derrumbes, deslaves y afectaciones", VERDE), width=12, sm=6, lg=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-users", "Atención a la población", f"{total_poblacion:,.0f} auxilios", "Incendios, rescates y salvamientos", VERDE), width=12, sm=6, lg=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-map-pin", "Zona de mayor impacto", top_comunidad_nombre, "Localidad con más incidencias", GUINDA), width=12, sm=6, lg=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-map-pins", "Comunidades atendidas", f"{comunidades_atendidas:,.0f} localidades", "Cobertura territorial del municipio", VERDE), width=12, sm=6, lg=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-percentage", "Cobertura rural", f"{pct_cobertura_rural:,.1f}%", "Atenciones fuera de la cabecera municipal", GUINDA), width=12, sm=6, lg=4, className="mb-3"),
        ])

        # =================================================================
        # 5. CONFIGURACIÓN DE GRÁFICAS (Comportamiento Mensual e Impacto Local)
        # =================================================================
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # Gráfica Temporal Mensual
        if col_mes:
            df_mes = df_pc.groupby(col_mes)[col_cantidad_sistema].sum().reset_index()
            df_mes[col_mes] = pd.Categorical(df_mes[col_mes], categories=orden_meses, ordered=True)
            df_mes = df_mes.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_mes = pd.DataFrame()

        if not df_mes.empty and df_mes[col_cantidad_sistema].sum() > 0:
            fig_mensual = px.line(
                df_mes, x=col_mes, y=col_cantidad_sistema, markers=True,
                color_discrete_sequence=[GUINDA],
                labels={col_cantidad_sistema: "Incidencias Atendidas", col_mes: ""}
            )
            fig_mensual.update_layout(
                margin=dict(l=40, r=15, t=10, b=15), plot_bgcolor="white", paper_bgcolor="white", height=260,
                yaxis={'gridcolor': '#f0f0f0', 'tickfont': dict(color=INK_SOFT)},
                xaxis={'tickfont': dict(color=INK_SOFT)},
                font=dict(family="Inter, sans-serif")
            )
            graph_left = dcc.Graph(figure=fig_mensual, config={'displayModeBar': False, "responsive": True}, style={"width": "100%"})
        else:
            graph_left = html.Div("ℹ️ No hay datos suficientes para graficar la tendencia temporal.",
                                   style={"padding": "40px 20px", "textAlign": "center", "color": INK_FAINT, "fontSize": "12px"})

        # Gráfica de Impacto Territorial por Comunidad (Top 5)
        if col_comunidad:
            df_com5 = df_pc.groupby(col_comunidad)[col_cantidad_sistema].sum().reset_index()
            df_com5 = df_com5[df_com5[col_cantidad_sistema] > 0].sort_values(by=col_cantidad_sistema, ascending=True).tail(5)
            df_com5[col_comunidad] = df_com5[col_comunidad].str.title()
        else:
            df_com5 = pd.DataFrame()

        if not df_com5.empty:
            fig_comunidades = px.bar(
                df_com5, x=col_cantidad_sistema, y=col_comunidad, orientation='h',
                color_discrete_sequence=[VERDE],
                labels={col_cantidad_sistema: "Total Reportes", col_comunidad: ""}
            )
            fig_comunidades.update_yaxes(tickvals=df_com5[col_comunidad], tickfont=dict(size=9, color=INK_SOFT))
            fig_comunidades.update_layout(
                margin=dict(l=140, r=15, t=10, b=15), plot_bgcolor="white", paper_bgcolor="white", height=260,
                xaxis={'gridcolor': '#f0f0f0', 'tickfont': dict(color=INK_SOFT)},
                font=dict(family="Inter, sans-serif")
            )
            graph_right = dcc.Graph(figure=fig_comunidades, config={'displayModeBar': False, "responsive": True}, style={"width": "100%"})
        else:
            graph_right = html.Div("ℹ️ No hay registros válidos para desglosar el impacto por comunidad.",
                                    style={"padding": "40px 20px", "textAlign": "center", "color": INK_FAINT, "fontSize": "12px"})

        graficas_row = dbc.Row([
            dbc.Col(_chart_panel("Histórico de incidencias mensuales", graph_left, color_top=GUINDA), md=6, className="mb-3"),
            dbc.Col(_chart_panel("Top 5 comunidades con mayor número de auxilios", graph_right, color_top=VERDE), md=6, className="mb-3"),
        ])

        # Gráfica de Tipología de Servicios (desglose por ACTIVIDAD, no solo por VARIABLE)
        if col_actividad:
            df_tipologia = df_pc.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
            df_tipologia = df_tipologia[df_tipologia[col_cantidad_sistema] > 0].sort_values(by=col_cantidad_sistema, ascending=True)
        else:
            df_tipologia = pd.DataFrame()

        if not df_tipologia.empty:
            colores_alternados = [GUINDA if i % 2 == 0 else VERDE for i in range(len(df_tipologia))]
            fig_tipologia = px.bar(
                df_tipologia, x=col_cantidad_sistema, y=col_actividad, orientation='h',
                text=df_tipologia[col_cantidad_sistema].apply(lambda x: f"{x:,.0f}"),
                labels={col_cantidad_sistema: "Total de Servicios", col_actividad: ""}
            )
            fig_tipologia.update_traces(marker_color=colores_alternados, textposition="outside", textfont=dict(size=10, color=INK_SOFT))
            fig_tipologia.update_yaxes(tickfont=dict(size=10, color=INK_SOFT))
            fig_tipologia.update_layout(
                margin=dict(l=140, r=30, t=10, b=15), plot_bgcolor="white", paper_bgcolor="white", height=280,
                xaxis={'gridcolor': '#f0f0f0', 'tickfont': dict(color=INK_SOFT)},
                font=dict(family="Inter, sans-serif")
            )
            panel_tipologia = _chart_panel(
                "Tipología de servicios de protección civil",
                dcc.Graph(figure=fig_tipologia, config={'displayModeBar': False, "responsive": True}, style={"width": "100%"}),
                color_top=GUINDA
            )
        else:
            panel_tipologia = html.Div()

        # =================================================================
        # 6bis. TABLA "DETALLE POR COMUNIDAD" (interactiva: orden + filtro)
        # =================================================================
        columnas_detalle = [c for c in [col_comunidad, col_mes, col_actividad, col_variable, col_atendidos] if c]
        if col_comunidad and columnas_detalle:
            df_detalle = df_pc[columnas_detalle].copy()
            df_detalle = df_detalle.rename(columns={col_comunidad: "COMUNIDAD"})
            df_detalle["COMUNIDAD"] = df_detalle["COMUNIDAD"].str.title()
            df_detalle = df_detalle.sort_values(by=col_atendidos, ascending=False) if col_atendidos else df_detalle

            columnas_mostrar = ["COMUNIDAD"] + [c for c in [col_mes, col_actividad, col_variable, col_atendidos] if c]
            etiquetas = {
                "COMUNIDAD": "Comunidad", col_mes: "Mes", col_actividad: "Actividad",
                col_variable: "Variable", col_atendidos: "Atendidos"
            }

            _cache_detalle_pc["data"] = df_detalle[columnas_mostrar]
            panel_detalle_comunidad = _tabla_detalle_comunidad(df_detalle, columnas_mostrar, etiquetas)
        else:
            panel_detalle_comunidad = html.Div()

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general"),
            kpis_row,
            _section_label("ti-list-details", "Tipología de servicios"),
            panel_tipologia,
            _section_label("ti-map-2", "Comportamiento e impacto territorial"),
            graficas_row,
            _section_label("ti-table", "Detalle por comunidad"),
            panel_detalle_comunidad,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Protección Civil: {str(e)}", color="danger", className="m-3")