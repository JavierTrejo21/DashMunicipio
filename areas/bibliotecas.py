# areas/bibliotecas.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA (misma que licencias_reglamentos.py)
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
# BLOQUES DE LAYOUT (idénticos a los usados en licencias_reglamentos.py)
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


def analizar_bibliotecas(df):
    """
    Módulo operativo — Bibliotecas y C.C.A.
    Misma estructura visual y colorimetría institucional (guinda/verde) que
    el módulo de Licencias y Reglamentos; la lógica analítica no cambia.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Bibliotecas llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # LISTA DE ORDEN DE MESES GLOBAL PARA LA FUNCIÓN
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # 1. Copiar y limpiar nombres de columnas
        df_bib = df.copy()
        df_bib.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_bib.columns]

        col_mes = next((c for c in df_bib.columns if "MES" in c), None)
        col_atendidos = next((c for c in df_bib.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_bib.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_bib.columns if "VARIABLE" in c), None)

        # 2. Conversión limpia de tipos de datos
        if col_atendidos:
            df_bib[col_atendidos] = pd.to_numeric(df_bib[col_atendidos], errors='coerce').fillna(0)
            df_bib["CANTIDAD"] = df_bib[col_atendidos]
            col_cantidad_sistema = "CANTIDAD"
        else:
            df_bib["CANTIDAD"] = 0
            col_cantidad_sistema = "CANTIDAD"

        if col_variable: df_bib[col_variable] = df_bib[col_variable].astype(str).str.strip().str.title()
        if col_actividad: df_bib[col_actividad] = df_bib[col_actividad].astype(str).str.strip().str.title()
        if col_mes: df_bib[col_mes] = df_bib[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. CÓMPUTO DE MATRÍCULA REAL (MÁXIMO MENSUAL POR TALLER)
        # =================================================================
        df_grupos = df_bib.groupby([col_actividad, col_variable, col_mes])[col_cantidad_sistema].sum().reset_index() if col_actividad and col_variable and col_mes else pd.DataFrame()

        if not df_grupos.empty:
            df_matricula_real = df_grupos.groupby([col_actividad, col_variable])[col_cantidad_sistema].max().reset_index()

            total_ninas_activos = df_matricula_real[df_matricula_real[col_variable].str.contains("niña|nina|feme", case=False, na=False)][col_cantidad_sistema].sum()
            total_ninos_activos = df_matricula_real[df_matricula_real[col_variable].str.contains("niño|nino|masc", case=False, na=False)][col_cantidad_sistema].sum()
            total_alumnos_unicos = total_ninas_activos + total_ninos_activos

            df_top_talleres = df_matricula_real.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
            top_taller_row = df_top_talleres.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0] if not df_top_talleres.empty else None
            top_programa = str(top_taller_row[col_actividad]) if top_taller_row is not None else "Sin registros"
        else:
            total_alumnos_unicos, total_ninas_activos, total_ninos_activos = 0, 0, 0
            top_programa = "No disponible"
            df_matricula_real = pd.DataFrame()

        if len(top_programa) > 35: top_programa = top_programa[:32] + "..."

        # =================================================================
        # 4. TARJETAS KPI (estilo institucional: badge-ring + borde superior)
        # =================================================================
        kpis_row = dbc.Row([
            dbc.Col(_kpi_card("ti-users", "Matrícula total activa", f"{total_alumnos_unicos:,.0f} niños(as)", "Periodo actual", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-star", "Programa con mayor matrícula", top_programa, "Taller / actividad líder", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-mood-smile", "Niñas registradas (únicas)", f"{total_ninas_activos:,.0f} alumnas", "Matrícula femenina", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-mood-smile", "Niños registrados (únicos)", f"{total_ninos_activos:,.0f} alumnos", "Matrícula masculina", VERDE), width=12, sm=6, lg=3, className="mb-3"),
        ])

        # =================================================================
        # 5. TABLA DE DETALLE (estilo institucional: header guinda, borde superior verde)
        # =================================================================
        if not df_matricula_real.empty:
            df_pivot = df_matricula_real.pivot(index=col_actividad, columns=col_variable, values=col_cantidad_sistema).fillna(0).reset_index()

            if "Niñas" not in df_pivot.columns: df_pivot["Niñas"] = 0
            if "Niños" not in df_pivot.columns: df_pivot["Niños"] = 0

            df_pivot["TOTAL ACTIVO"] = df_pivot["Niñas"] + df_pivot["Niños"]
            df_pivot = df_pivot.sort_values(by="TOTAL ACTIVO", ascending=False)

            th_style = {"fontSize": "10.5px", "color": "#fff", "textAlign": "left", "padding": "10px 14px",
                        "fontWeight": "700", "letterSpacing": ".04em", "textTransform": "uppercase",
                        "backgroundColor": GUINDA_DARK, "borderBottom": f"1px solid {LINE}"}
            td_style = {"fontSize": "12.5px", "color": INK, "padding": "10px 14px", "borderBottom": f"1px solid {LINE}"}

            filas_tabla = []
            for i, (_, r) in enumerate(df_pivot.iterrows()):
                bg = "#FAF8F4" if i % 2 == 1 else CARD
                filas_tabla.append(html.Tr([
                    html.Td(r[col_actividad], style={**td_style, "backgroundColor": bg, "fontWeight": "600"}),
                    html.Td(f"{r['Niñas']:,.0f}", style={**td_style, "backgroundColor": bg, "textAlign": "center", "fontWeight": "600"}),
                    html.Td(f"{r['Niños']:,.0f}", style={**td_style, "backgroundColor": bg, "textAlign": "center", "fontWeight": "600"}),
                    html.Td(f"{r['TOTAL ACTIVO']:,.0f}", style={**td_style, "backgroundColor": bg, "textAlign": "center", "fontWeight": "700", "color": GUINDA_DARK}),
                ]))

            # Fila de totales generales
            filas_tabla.append(html.Tr([
                html.Td("TOTAL MATRÍCULA MUNICIPAL", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK}),
                html.Td(f"{total_ninas_activos:,.0f}", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK, "textAlign": "center"}),
                html.Td(f"{total_ninos_activos:,.0f}", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": VERDE_DARK, "textAlign": "center"}),
                html.Td(f"{total_alumnos_unicos:,.0f}", style={**td_style, "fontWeight": "700", "color": "#fff", "backgroundColor": GUINDA, "textAlign": "center"}),
            ]))

            tabla_layout = html.Div(
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Taller / Actividad Educativa", style=th_style),
                        html.Th("Niñas", style={**th_style, "textAlign": "center"}),
                        html.Th("Niños", style={**th_style, "textAlign": "center"}),
                        html.Th("Total Inscritos", style={**th_style, "textAlign": "center", "backgroundColor": GUINDA}),
                    ])),
                    html.Tbody(filas_tabla)
                ], style={"width": "100%", "margin": "0", "borderCollapse": "collapse"}),
                style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
                       "borderTop": f"3px solid {VERDE}", "overflow": "hidden"}
            )
        else:
            tabla_layout = html.Div()

        # =================================================================
        # 6. GRÁFICA: TENDENCIA HISTÓRICA MENSUAL (mismos colores institucionales)
        # =================================================================
        if col_mes and col_variable:
            df_lineas = df_bib.groupby([col_mes, col_variable])[col_cantidad_sistema].sum().reset_index()
            df_lineas[col_mes] = pd.Categorical(df_lineas[col_mes], categories=orden_meses, ordered=True)
            df_lineas = df_lineas.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_lineas = pd.DataFrame()

        if not df_lineas.empty and df_lineas[col_cantidad_sistema].sum() > 0:
            fig_comparativa = px.line(
                df_lineas, x=col_mes, y=col_cantidad_sistema, color=col_variable, markers=True,
                color_discrete_map={"Niñas": GUINDA, "Niños": VERDE},
                labels={col_cantidad_sistema: "Asistencias", col_mes: "", col_variable: "Segmento"}
            )
            fig_comparativa.update_layout(
                margin=dict(l=40, r=15, t=10, b=15),
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=260,
                yaxis={'gridcolor': '#f0f0f0', 'tickfont': dict(color=INK_SOFT)},
                xaxis={'tickfont': dict(color=INK_SOFT)},
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter", size=11)),
                font=dict(family="Inter, sans-serif")
            )
            seccion_grafica = _chart_panel("Comportamiento histórico mensual de asistencia", fig_comparativa, color_top=GUINDA)
        else:
            seccion_grafica = html.Div("ℹ️ No hay registros suficientes para estructurar el histórico.",
                                        style={"padding": "20px", "color": INK_FAINT, "fontSize": "12px"})

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general"),
            kpis_row,
            _section_label("ti-table", "Detalle por taller"),
            tabla_layout,
            _section_label("ti-chart-line", "Tendencia mensual"),
            seccion_grafica,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Bibliotecas: {str(e)}", color="danger", className="m-3")