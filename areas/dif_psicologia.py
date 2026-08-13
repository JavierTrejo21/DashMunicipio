# areas/dif_psicologia.py
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


def analizar_dif_psicologia(df):
    """
    Módulo híbrido de Alto Impacto para DIF Psicología.
    - Alineado con la paleta institucional guinda/verde del sistema.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de DIF Psicología llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_psic = df.copy()
        df_psic.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_psic.columns]

        col_actividad = next((c for c in df_psic.columns if "ACTIVIDAD" in c), None)
        col_atendidos = next((c for c in df_psic.columns if "ATENDID"   in c or "CANTIDAD" in c), None)
        col_variable  = next((c for c in df_psic.columns if "VARIABLE"  in c), None)

        # Conversión de tipos de datos
        if col_atendidos:
            df_psic[col_atendidos] = pd.to_numeric(df_psic[col_atendidos], errors='coerce').fillna(0)
            col_cantidad_sistema = col_atendidos
        else:
            df_psic["CANTIDAD_GENERICA"] = 0
            col_cantidad_sistema = "CANTIDAD_GENERICA"

        if col_variable:  df_psic[col_variable]  = df_psic[col_variable].astype(str).str.strip().str.title()
        if col_actividad: df_psic[col_actividad] = df_psic[col_actividad].astype(str).str.strip().str.title()

        # Separación por bloques operativos (Anualizado sin meses)
        df_temas = df_psic[df_psic[col_variable].str.contains("Tema|Trastorno",       case=False, na=False)]
        df_demo  = df_psic[df_psic[col_variable].str.contains("Demografica|Paciente", case=False, na=False)]

        # =================================================================
        # 2. CÓMPUTO DE KPIs
        # =================================================================
        total_consultas = df_temas[col_cantidad_sistema].sum()
        total_pacientes = df_demo[col_cantidad_sistema].sum()

        df_top_trastorno = df_temas.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        if not df_top_trastorno.empty:
            top_row       = df_top_trastorno.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0]
            top_incidencia = str(top_row[col_actividad])
            if len(top_incidencia) > 30:
                top_incidencia = top_incidencia[:27] + "..."
        else:
            top_incidencia = "N/A"

        # ==========================================================
        # KPI CARDS — estilo institucional badge-ring + borde superior
        # ==========================================================
        seccion_kpis = dbc.Row([
            dbc.Col(_kpi_card("ti-stethoscope",  "Total consultas clínicas",  f"{int(total_consultas):,} sesiones", "Periodo actual",       VERDE),  width=12, sm=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-users",         "Ciudadanos atendidos",      f"{int(total_pacientes):,} personas", "Pacientes únicos",     GUINDA), width=12, sm=4, className="mb-3"),
            dbc.Col(_kpi_card("ti-brain",         "Principal diagnóstico",     top_incidencia,                       "Mayor incidencia",     VERDE),  width=12, sm=4, className="mb-3"),
        ], className="g-2")

        # =================================================================
        # 3. TABLA DE RESUMEN DEMOGRÁFICO — scroll si supera 10 filas
        # =================================================================
        df_demo_agrupado = df_demo.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_demo_agrupado = df_demo_agrupado.sort_values(by=col_cantidad_sistema, ascending=False)

        th_style = {
            "fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
            "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
            "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}"
        }
        td_style = {"fontSize": "12.5px", "color": INK, "padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}

        filas_tabla_demo = []
        for i, (_, r) in enumerate(df_demo_agrupado.iterrows()):
            bg = "#FAF8F4" if i % 2 == 1 else CARD
            filas_tabla_demo.append(html.Tr([
                html.Td(r[col_actividad],                     style={**td_style, "backgroundColor": bg, "fontWeight": "600"}),
                html.Td(f"{r[col_cantidad_sistema]:,.0f}",    style={**td_style, "backgroundColor": bg,
                                                                      "textAlign": "center", "fontWeight": "700", "color": GUINDA_DARK}),
            ]))

        # Fila de totales
        filas_tabla_demo.append(html.Tr([
            html.Td("TOTAL PACIENTES ÚNICOS", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
            html.Td(f"{int(total_pacientes):,}",  style={**td_style, "fontWeight": "700", "color": "#fff",
                                                          "backgroundColor": GUINDA, "textAlign": "center"}),
        ]))

        max_height   = "320px" if len(df_demo_agrupado) > 10 else None
        scroll_style = {"overflowY": "auto", "maxHeight": max_height} if max_height else {}

        tabla_demo = html.Div(
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Grupo Vulnerable / Edad y Género", style={**th_style, "width": "75%"}),
                    html.Th("Total",                            style={**th_style, "textAlign": "center",
                                                                       "backgroundColor": GUINDA, "width": "25%"}),
                ])),
                html.Tbody(
                    filas_tabla_demo if filas_tabla_demo
                    else [html.Tr([html.Td("Sin registros", colSpan=2,
                                           style={"textAlign": "center", "color": INK_FAINT, "padding": "16px"})])]
                ),
            ], style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
            style={
                "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
                "borderTop": f"3px solid {VERDE}", "overflow": "hidden",
                **scroll_style
            }
        )

        # =================================================================
        # 4. EMBUDO DE PROBLEMÁTICAS — colores institucionales
        # =================================================================
        df_temas_agrupado = df_temas.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_temas_agrupado = df_temas_agrupado.sort_values(by=col_cantidad_sistema, ascending=False)

        fig_embudo = px.funnel(
            df_temas_agrupado, x=col_cantidad_sistema, y=col_actividad,
            color_discrete_sequence=[GUINDA],
            labels={col_cantidad_sistema: "Casos", col_actividad: "Diagnóstico"}
        )
        fig_embudo.update_layout(
            margin=dict(l=10, r=20, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=300,
            font=dict(family="Inter, sans-serif", size=11, color=INK)
        )
        fig_embudo.update_yaxes(automargin=True)

        panel_embudo = _chart_panel(
            "Embudo de problemáticas y salud mental detectada",
            fig_embudo,
            color_top=GUINDA
        )

        # =================================================================
        # 5. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-brain", "Resumen general"),
            seccion_kpis,
            dbc.Row([
                dbc.Col([
                    _section_label("ti-table", "Perfil y matrícula de pacientes"),
                    tabla_demo,
                ], width=12, lg=5, className="mb-3"),
                dbc.Col([
                    _section_label("ti-chart-sankey", "Problemáticas detectadas"),
                    panel_embudo,
                ], width=12, lg=7, className="mb-3"),
            ], className="g-3"),
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error en la consolidación del módulo de DIF Psicología: {str(e)}", color="danger", className="m-3")