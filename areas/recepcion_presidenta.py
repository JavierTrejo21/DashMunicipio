# areas/recepcion_presidenta.py
import pandas as pd
import unicodedata
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA
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


def limpiar_texto(texto):
    if not isinstance(texto, str):
        return str(texto)
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper().strip()


# ==========================================================
# BLOQUES DE LAYOUT
# ==========================================================

def _fuentes_e_iconos():
    """Google Fonts + Tabler Icons"""
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


def _rubro_card(nombre_rubro, monto_rubro, ben_rubro, color=GUINDA):
    return html.Div([
        html.Div([
            html.I(className="ti ti-tag", style={"color": color, "fontSize": "14px"}),
            html.Span(nombre_rubro, style={
                "fontSize": "11.5px", "fontWeight": "700", "color": INK,
                "marginLeft": "6px"
            }),
        ], style={
            "display": "flex", "alignItems": "center", "paddingBottom": "10px",
            "marginBottom": "10px", "borderBottom": f"1px solid {LINE}"
        }),
        html.Div(f"${monto_rubro:,.2f}", style={
            "fontWeight": "700", "fontSize": "16px", "color": color, "marginBottom": "4px"
        }),
        html.Div([
            html.I(className="ti ti-users", style={"color": INK_FAINT, "fontSize": "12px"}),
            html.Span(f" Beneficiarios: {ben_rubro:,.0f} civ.", style={
                "fontSize": "10.5px", "color": INK_SOFT, "marginLeft": "4px"
            }),
        ]),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {color}", "padding": "14px 16px", "height": "100%", "boxSizing": "border-box"
    })


# ==========================================================
# MÓDULO OPERATIVO — RECEPCIÓN / RENDICIÓN DE CUENTAS
# ==========================================================

def analizar_recepcion_presidenta(df):
    """
    Módulo operativo — Recepción y Rendición de Cuentas de la Presidenta.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Recepción / Rendición de Cuentas no contiene registros válidos.", color="warning", className="m-3")

    try:
        df_rec = df.copy()

        # Normalizar nombres de columnas
        df_rec.columns = [limpiar_texto(c) for c in df_rec.columns]

        # Identificación flexible de columnas clave
        col_rubro = next((c for c in df_rec.columns if "RUBRO" in c or "CATEGORIA" in c or "TEMA" in c or "ASUNTO" in c), df_rec.columns[2])
        col_recurso = next((c for c in df_rec.columns if "INVERSION" in c or "MONTO" in c or "COSTO" in c or "GASTO" in c or "RECURSO" in c), None)
        col_beneficiarios = next((c for c in df_rec.columns if "BENEFICIARIO" in c or "CIV" in c or "PERSONAS" in c), None)
        col_comunidad = next((c for c in df_rec.columns if "COMUNIDAD" in c or "LOCALIDAD" in c or "MUNICIPIO" in c), None)
        col_mes = next((c for c in df_rec.columns if "MES" in c or "FECHA" in c), None)

        # Limpieza numérica robusta para recurso y beneficiarios
        if col_recurso:
            df_rec[col_recurso] = pd.to_numeric(
                df_rec[col_recurso].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors='coerce'
            ).fillna(0)
        else:
            df_rec["__RECURSO__"] = 0.0
            col_recurso = "__RECURSO__"

        if col_beneficiarios:
            df_rec[col_beneficiarios] = pd.to_numeric(
                df_rec[col_beneficiarios].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors='coerce'
            ).fillna(0)
        else:
            df_rec["__BENEFICIARIOS__"] = 0
            col_beneficiarios = "__BENEFICIARIOS__"

        # Normalizar texto de comunidad para evitar duplicados por espacios (ej. "CHAPULHUACAN " vs "CHAPULHUACAN")
        if col_comunidad:
            df_rec[col_comunidad] = df_rec[col_comunidad].apply(limpiar_texto)

        # =================================================================
        # CONTROL DE BENEFICIARIOS (Evitar inflar el número por repetición)
        # =================================================================
        # Si una comunidad aparece múltiples veces con la misma cantidad exacta de beneficiarios 
        # o eventos similares, aplicamos una agregación inteligente (ej. max por evento/comunidad o suma única de alcance)
        if col_comunidad:
            # Agrupamos por comunidad y categoría para sumar de forma limpia y evitar duplicidades forzadas
            df_beneficiarios_unicos = df_rec.groupby([col_comunidad, col_rubro], as_index=False)[col_beneficiarios].max()
            beneficiarios_totales = df_beneficiarios_unicos[col_beneficiarios].sum()
        else:
            beneficiarios_totales = df_rec[col_beneficiarios].sum()

        recurso_total = df_rec[col_recurso].sum()
        gestiones_atendidas = len(df_rec)
        comunidades_atendidas = df_rec[col_comunidad].nunique() if col_comunidad else 0

        # =================================================================
        # TARJETAS KPI (Recurso entregado en lugar de inversión)
        # =================================================================
        kpis_row = dbc.Row([
            dbc.Col(_kpi_card("ti-cash", "Recurso entregado", f"${recurso_total:,.2f}", "Apoyo poblacional", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-users", "Beneficiarios atendidos", f"{beneficiarios_totales:,.0f} civ.", "Alcance depurado", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-map-pin", "Comunidades alcanzadas", f"{comunidades_atendidas:,.0f}", "Cobertura municipal", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-clipboard-check", "Gestiones atendidas", f"{gestiones_atendidas:,.0f}", "Total de registros", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
        ])

        # Agrupación precisa por Rubros
        df_rubros = df_rec.groupby(col_rubro, as_index=False).agg({
            col_recurso: 'sum',
            col_beneficiarios: 'sum'
        }).sort_values(by=col_recurso, ascending=False)

        total_rec_val = df_rubros[col_recurso].sum() if recurso_total > 0 else 1
        df_rubros['PORCENTAJE'] = (df_rubros[col_recurso] / total_rec_val) * 100

        # =================================================================
        # GRÁFICA DE BARRAS — DISTRIBUCIÓN POR RUBRO
        # =================================================================
        fig_barras = px.bar(
            df_rubros,
            x=col_rubro,
            y=col_recurso,
            text=df_rubros.apply(lambda r: f"{r['PORCENTAJE']:.1f}%<br>${r[col_recurso]:,.0f}", axis=1),
            color_discrete_sequence=[GUINDA],
            labels={col_recurso: "Recurso Entregado", col_rubro: ""}
        )
        fig_barras.update_traces(textposition='inside', insidetextanchor='middle', textfont=dict(color="white", size=10))
        fig_barras.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=300,
            margin=dict(l=20, r=15, t=10, b=70),
            xaxis=dict(showgrid=False, title="", tickangle=-30, tickfont=dict(color=INK_SOFT)),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="", tickfont=dict(color=INK_SOFT)),
            font=dict(family="Inter, sans-serif")
        )

        # =================================================================
        # GRÁFICA DE LÍNEA — HISTÓRICO MENSUAL DE RECURSO
        # =================================================================
        if col_mes and not df_rec[col_mes].isna().all():
            df_meses = df_rec.groupby(col_mes, as_index=False)[col_recurso].sum()
        else:
            df_meses = pd.DataFrame({
                'MES': ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio"],
                col_recurso: [0, 0, 0, 0, 0, 0, 0]
            })
            col_mes = 'MES'

        fig_linea = px.line(
            df_meses,
            x=col_mes,
            y=col_recurso,
            markers=True,
            text=df_meses[col_recurso].apply(lambda x: f"${x:,.0f}"),
            color_discrete_sequence=[VERDE],
            labels={col_recurso: "Recurso Entregado", col_mes: ""}
        )
        fig_linea.update_traces(textposition="top center", line=dict(width=3), textfont=dict(size=10, color=INK_SOFT))
        fig_linea.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=300,
            margin=dict(l=20, r=15, t=10, b=60),
            xaxis=dict(showgrid=False, title="", tickangle=-25, tickfont=dict(color=INK_SOFT)),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="", tickfont=dict(color=INK_SOFT)),
            font=dict(family="Inter, sans-serif")
        )

        graficas_row = dbc.Row([
            dbc.Col(_chart_panel("Distribución y porcentaje por principales rubros", fig_barras, color_top=GUINDA), md=7, className="mb-3"),
            dbc.Col(_chart_panel("Histórico mensual de entrega de recursos", fig_linea, color_top=VERDE), md=5, className="mb-3"),
        ])

        # =================================================================
        # TARJETAS INFERIORES — DESGLOSE POR RUBRO
        # =================================================================
        tarjetas_rubros_cols = []
        for i, (_, row) in enumerate(df_rubros.iterrows()):
            nombre_rubro = str(row[col_rubro])
            monto_rubro = row[col_recurso]
            ben_rubro = row[col_beneficiarios]
            color_tarjeta = GUINDA if i % 2 == 0 else VERDE

            tarjetas_rubros_cols.append(
                dbc.Col(_rubro_card(nombre_rubro, monto_rubro, ben_rubro, color_tarjeta),
                        width=12, sm=6, md=3, className="mb-3")
            )

        grid_tarjetas_rubros = dbc.Row(tarjetas_rubros_cols)

        # =================================================================
        # LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general de apoyos"),
            kpis_row,
            _section_label("ti-chart-area", "Comportamiento e histórico"),
            graficas_row,
            _section_label("ti-list-details", "Desglose detallado por rubro"),
            grid_tarjetas_rubros,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Recepción / Rendición de Cuentas: {str(e)}", color="danger", className="m-3")