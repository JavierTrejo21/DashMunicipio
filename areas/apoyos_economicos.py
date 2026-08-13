# areas/apoyos_economicos.py
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


def analizar_apoyos_economicos(df):
    """Análisis estructurado y ejecutivo para DIF Apoyos Económicos con colorimetría institucional."""

    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()

    columnas_reales = df.columns.tolist()

    col_actividad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["ACTIVIDAD", "CAT", "APOYO", "CONCEPTO"])), columnas_reales[0] if columnas_reales else None)
    col_inversion = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["INV", "COSTO", "MONTO", "IMPORTE"])), None)
    col_beneficiarios = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["BENEF", "PERSONAS", "POBLACION"])), None)

    if not col_actividad:
        return dbc.Alert("⚠️ No se encontró una columna de actividad válida para Apoyos Económicos.", color="danger", className="m-3")

    df_limpio = pd.DataFrame()
    df_limpio['Actividad'] = df[col_actividad].astype(str).str.strip().str.title()

    if col_inversion:
        serie_inv = df[col_inversion].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
        serie_inv = serie_inv.replace(['-', ''], '0')
        df_limpio['Inversión'] = pd.to_numeric(serie_inv, errors='coerce').fillna(0)
    else:
        df_limpio['Inversión'] = 0

    df_limpio['Beneficiarios'] = pd.to_numeric(df[col_beneficiarios], errors='coerce').fillna(0) if col_beneficiarios else 0

    df_limpio = df_limpio[
        (df_limpio['Actividad'] != '') &
        (df_limpio['Actividad'] != 'Nan')
    ]

    total_inversion = df_limpio['Inversión'].sum()
    total_beneficiarios = df_limpio['Beneficiarios'].sum()

    # =================================================================
    # KPI CARDS (estilo institucional: badge-ring + borde superior)
    # =================================================================
    kpis_row = dbc.Row([
        dbc.Col(_kpi_card("ti-cash", "Inversión total en apoyos", f"${total_inversion:,.2f}", "Monto ejercido en el periodo", VERDE), width=12, sm=6, className="mb-3"),
        dbc.Col(_kpi_card("ti-users", "Total de beneficiarios", f"{int(total_beneficiarios):,} personas", "Población atendida", GUINDA), width=12, sm=6, className="mb-3"),
    ])

    # =================================================================
    # AGRUPACIÓN POR ACTIVIDAD
    # =================================================================
    df_grouped = df_limpio.groupby('Actividad').agg({'Inversión': 'sum', 'Beneficiarios': 'sum'}).reset_index()
    df_grouped['Porcentaje'] = (df_grouped['Inversión'] / total_inversion * 100) if total_inversion > 0 else 0
    df_grouped = df_grouped.sort_values(by='Inversión', ascending=False).reset_index(drop=True)

    # =================================================================
    # TABLA EJECUTIVA (estilo institucional: header guinda, borde superior verde, scroll)
    # =================================================================
    th_style = {
        "fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
        "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
        "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}",
        "position": "sticky", "top": "0", "zIndex": "1"
    }
    td_style = {"fontSize": "12.5px", "color": INK, "padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}

    filas_tabla = []
    for i, (_, row) in enumerate(df_grouped.iterrows()):
        bg = "#FAF8F4" if i % 2 == 1 else CARD
        pct = row['Porcentaje']
        filas_tabla.append(html.Tr([
            html.Td([
                html.Div(row['Actividad'], style={"fontWeight": "600", "color": INK, "fontSize": "12.5px", "marginBottom": "4px"}),
                html.Div([
                    html.Div(style={
                        "height": "4px", "borderRadius": "2px",
                        "width": f"{min(pct, 100):.1f}%",
                        "backgroundColor": VERDE,
                        "transition": "width .4s ease"
                    })
                ], style={"backgroundColor": LINE, "borderRadius": "2px", "height": "4px"})
            ], style={**td_style, "backgroundColor": bg, "width": "40%"}),
            html.Td(f"{int(row['Beneficiarios']):,}", style={**td_style, "backgroundColor": bg, "textAlign": "center"}),
            html.Td(f"${row['Inversión']:,.2f}", style={**td_style, "backgroundColor": bg, "textAlign": "right", "fontWeight": "700", "color": VERDE_DARK}),
            html.Td(f"{pct:.1f}%", style={**td_style, "backgroundColor": bg, "textAlign": "center", "fontWeight": "700", "color": GUINDA_DARK}),
        ]))

    fila_total = html.Tr([
        html.Td("TOTAL GENERAL DE APOYOS ECONÓMICOS", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
        html.Td(f"{int(total_beneficiarios):,}", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK, "textAlign": "center"}),
        html.Td(f"${total_inversion:,.2f}", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": GUINDA, "textAlign": "right"}),
        html.Td("100%", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": GUINDA, "textAlign": "center"}),
    ])

    tabla_layout = html.Div([
        # Encabezado fijo
        html.Table([
            html.Thead(html.Tr([
                html.Th("Rubro / Actividad", style={**th_style, "width": "40%"}),
                html.Th("Beneficiarios", style={**th_style, "textAlign": "center", "width": "20%"}),
                html.Th("Inversión Total", style={**th_style, "textAlign": "right", "width": "25%"}),
                html.Th("Participación", style={**th_style, "textAlign": "center", "width": "15%", "backgroundColor": GUINDA}),
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
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {VERDE}", "overflow": "hidden"
    })

    # =================================================================
    # LAYOUT CONSOLIDADO FINAL
    # =================================================================
    return html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-chart-bar", "Resumen general"),
        kpis_row,
        _section_label("ti-table", "Síntesis consolidada de apoyos económicos"),
        tabla_layout,
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})