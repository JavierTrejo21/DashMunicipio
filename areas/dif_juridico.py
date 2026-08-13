import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

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


def analizar_dif_juridico(df):
    """Módulo estructurado para DIF Jurídico con tarjetas de resumen y desglose de servicios."""

    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()

    columnas_reales = df.columns.tolist()

    col_actividad = next((c for c in columnas_reales if "ACTIVIDAD" in str(c).upper()), "Actividad")
    col_cantidad  = next((c for c in columnas_reales if "CANTIDAD"  in str(c).upper()), "Cantidad")
    col_mes       = next((c for c in columnas_reales if "MES"       in str(c).upper()), "Mes")

    df_limpio = pd.DataFrame()
    df_limpio['Actividad'] = df[col_actividad].astype(str).str.strip() if col_actividad in df.columns else "General"
    df_limpio['Cantidad']  = pd.to_numeric(df[col_cantidad], errors='coerce').fillna(0) if col_cantidad in df.columns else 0
    df_limpio['Mes']       = df[col_mes].astype(str).str.strip().str.title() if col_mes in df.columns else "General"

    # ── Métricas clave globales ────────────────────────────────────────────
    total_asesorias      = df_limpio[df_limpio['Actividad'].str.contains("asesorias juridicas",  case=False, na=False)]['Cantidad'].sum()
    total_canalizaciones = df_limpio[df_limpio['Actividad'].str.contains("Canalización",         case=False, na=False)]['Cantidad'].sum()
    total_pensiones      = df_limpio[df_limpio['Actividad'].str.contains("pensión alimenticia",  case=False, na=False)]['Cantidad'].sum()
    total_registros_gral = df_limpio['Cantidad'].sum()

    # ==========================================================
    # KPI CARDS — estilo institucional badge-ring + borde superior
    # ==========================================================
    kpis_row = dbc.Row([
        dbc.Col(_kpi_card("ti-gavel",        "Total de asesorías jurídicas",                    f"{int(total_asesorias):,} asesorías",  "Periodo actual",   VERDE),  width=12, sm=6, lg=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-arrows-right", "Casos canalizados a otras instancias",            f"{int(total_canalizaciones):,} casos", "Derivaciones",     GUINDA), width=12, sm=6, lg=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-report",       "Trámites de pensión alimenticia",                 f"{int(total_pensiones):,} trámites",   "Gestiones activas", VERDE),  width=12, sm=6, lg=4, className="mb-3"),
    ])

    # ==========================================================
    # TABLA CONSOLIDADA — con scroll si supera 10 filas
    # ==========================================================
    df_resumen = df_limpio.groupby('Actividad')['Cantidad'].sum().reset_index()
    df_resumen = df_resumen.sort_values(by='Cantidad', ascending=False)

    th_style = {
        "fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
        "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
        "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}"
    }
    td_style = {"fontSize": "12.5px", "color": INK, "padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}

    filas_tabla = []
    for i, (_, row) in enumerate(df_resumen.iterrows()):
        bg = "#FAF8F4" if i % 2 == 1 else CARD
        filas_tabla.append(html.Tr([
            html.Td(row['Actividad'],           style={**td_style, "backgroundColor": bg, "fontWeight": "600"}),
            html.Td(f"{int(row['Cantidad']):,}", style={**td_style, "backgroundColor": bg, "textAlign": "center",
                                                        "fontWeight": "700", "color": GUINDA_DARK}),
        ]))

    # Fila de totales
    filas_tabla.append(html.Tr([
        html.Td("TOTAL GENERAL", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
        html.Td(f"{int(total_registros_gral):,}", style={**td_style, "fontWeight": "700", "color": "#fff",
                                                          "backgroundColor": GUINDA, "textAlign": "center"}),
    ]))

    # Scroll vertical cuando hay más de 10 filas de datos
    max_height = "380px" if len(df_resumen) > 10 else None
    scroll_style = {"overflowY": "auto", "maxHeight": max_height} if max_height else {}

    tabla_consolidada = html.Div(
        html.Table([
            html.Thead(html.Tr([
                html.Th("Descripción de la Actividad / Servicio", style=th_style),
                html.Th("Total Acumulado", style={**th_style, "textAlign": "center", "backgroundColor": GUINDA}),
            ])),
            html.Tbody(
                filas_tabla if filas_tabla
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

    # ==========================================================
    # TARJETA DE CONTEXTO OPERATIVO — panel informativo institucional
    # ==========================================================
    card_info = html.Div([
        html.Div([
            html.I(className="ti ti-info-circle", style={"color": VERDE, "fontSize": "15px"}),
            html.Span("Enfoque del módulo jurídico", style={
                "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "13px",
                "letterSpacing": ".03em", "color": GUINDA_DARK, "textTransform": "uppercase"
            }),
        ], style={"display": "flex", "alignItems": "center", "gap": "8px",
                  "borderBottom": f"1px solid {LINE}", "paddingBottom": "12px", "marginBottom": "14px"}),

        html.P(
            "El departamento jurídico registra la atención de asesorías, representación legal, "
            "gestión de pensiones, canalizaciones a otras instancias y protección de derechos vulnerados.",
            style={"fontSize": "12px", "color": INK_SOFT, "lineHeight": "1.6", "marginBottom": "12px"}
        ),
        html.Ul([
            html.Li("Control de atención diferenciada por género y grupos vulnerables.",
                    style={"fontSize": "11.5px", "color": INK_SOFT, "marginBottom": "6px"}),
            html.Li("Seguimiento a visitas domiciliarias y actas de tutela.",
                    style={"fontSize": "11.5px", "color": INK_SOFT, "marginBottom": "6px"}),
            html.Li(f"Volumen general acumulado en el periodo: {int(total_registros_gral):,} registros operativos.",
                    style={"fontSize": "11.5px", "color": GUINDA_DARK, "fontWeight": "600"}),
        ], style={"paddingLeft": "18px", "margin": "0"}),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {GUINDA}", "padding": "20px 22px",
        "boxShadow": "0 1px 2px rgba(84,19,42,.05)", "height": "100%", "boxSizing": "border-box"
    })

    # ==========================================================
    # LAYOUT CONSOLIDADO FINAL
    # ==========================================================
    return html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-scale", "Resumen general"),
        kpis_row,
        dbc.Row([
            dbc.Col([
                _section_label("ti-table", "Consolidado de actividades"),
                tabla_consolidada,
            ], md=7, className="mb-3"),
            dbc.Col([
                _section_label("ti-info-circle", "Contexto operativo"),
                card_info,
            ], md=5, className="mb-3"),
        ]),
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})