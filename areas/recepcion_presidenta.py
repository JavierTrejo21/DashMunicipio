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

POBLACION_TOTAL_MUNICIPIO = 22903

# Diccionario para orden cronológico de meses en español
MESES_ORDEN = {
    'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4,
    'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
    'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12
}


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


def _rubro_card(nombre_rubro, pct_inversion, ben_rubro, pct_beneficiarios, color=GUINDA):
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
        html.Div(f"{pct_inversion:.1f}% de Inversión", style={
            "fontWeight": "700", "fontSize": "15px", "color": color, "marginBottom": "6px"
        }),
        html.Div([
            html.I(className="ti ti-users", style={"color": INK_FAINT, "fontSize": "12px"}),
            html.Span(f" {ben_rubro:,.0f} Ciudadanos ({pct_beneficiarios:.1f}% del total)", style={
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

        # Limpieza numérica robusta
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

        if col_comunidad:
            df_rec[col_comunidad] = df_rec[col_comunidad].apply(limpiar_texto)

        # Control de beneficiarios unificados por comunidad y rubro
        if col_comunidad:
            df_beneficiarios_unicos = df_rec.groupby([col_comunidad, col_rubro], as_index=False)[col_beneficiarios].max()
            beneficiarios_totales = df_beneficiarios_unicos[col_beneficiarios].sum()
        else:
            beneficiarios_totales = df_rec[col_beneficiarios].sum()

        recurso_total = df_rec[col_recurso].sum()

        # Cálculo dinámico del porcentaje de la población atendida respecto al total municipal (22,903)
        pct_poblacion_total = (beneficiarios_totales / POBLACION_TOTAL_MUNICIPIO) * 100 if POBLACION_TOTAL_MUNICIPIO > 0 else 0

        # =================================================================
        # TARJETAS KPI PRINCIPALES
        # =================================================================
        kpis_row = dbc.Row([
            dbc.Col(_kpi_card("ti-cash", "Recurso entregado", f"${recurso_total:,.2f}", "Cantidad total entregada en diferentes rubros.", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-users", "Población Atendida", f"{beneficiarios_totales:,.0f} Ciudadanos.", f"{pct_poblacion_total:.1f}% de la población total del municipio (22,903 Ciudadanos).", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-user-check", "Audiencias atendidas por la presidenta", "1,427", "Atención directa a personas y Comisiones de comunidades.", VERDE), width=12, sm=6, lg=3, className="mb-3"),
            dbc.Col(_kpi_card("ti-gift", "Apoyos en especie entregados", "175", "Material de construcción, implementos para el campo, etc.", GUINDA), width=12, sm=6, lg=3, className="mb-3"),
        ])

        # Agrupación precisa por Rubros
        df_rubros = df_rec.groupby(col_rubro, as_index=False).agg({
            col_recurso: 'sum',
            col_beneficiarios: 'sum'
        }).sort_values(by=col_recurso, ascending=False)

        total_rec_val = recurso_total if recurso_total > 0 else 1
        total_ben_val = beneficiarios_totales if beneficiarios_totales > 0 else 1

        df_rubros['PORCENTAJE_INV'] = (df_rubros[col_recurso] / total_rec_val) * 100
        df_rubros['PORCENTAJE_BEN'] = (df_rubros[col_beneficiarios] / total_ben_val) * 100

        # Omitir rubros con 0% o sin inversión activa para evitar tarjetas vacías
        df_rubros = df_rubros[df_rubros['PORCENTAJE_INV'] > 0]

        # Histórico mensual y ordenamiento cronológico por mes
        if col_mes and not df_rec[col_mes].isna().all():
            df_rec['__MES_LIMPIO__'] = df_rec[col_mes].apply(limpiar_texto)
            df_meses = df_rec.groupby('__MES_LIMPIO__', as_index=False)[col_recurso].sum()
            df_meses['ORDEN'] = df_meses['__MES_LIMPIO__'].map(MESES_ORDEN).fillna(99)
            df_meses = df_meses.sort_values('ORDEN').drop(columns=['ORDEN'])
            df_meses = df_meses.rename(columns={'__MES_LIMPIO__': col_mes})
        else:
            df_meses = pd.DataFrame({
                'MES': ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"],
                col_recurso: [0]*12
            })
            col_mes = 'MES'

        promedio_mensual = df_meses[col_recurso].mean() if len(df_meses) > 0 else 0

        fig_linea = px.line(
            df_meses,
            x=col_mes,
            y=col_recurso,
            markers=True,
            text=df_meses[col_recurso].apply(lambda x: f"${x:,.0f}"),
            color_discrete_sequence=[VERDE],
            labels={col_recurso: "Recurso Entregado", col_mes: ""}
        )
        fig_linea.add_hline(
            y=promedio_mensual,
            line_dash="dash",
            line_color=GUINDA,
            annotation_text=f"Promedio: ${promedio_mensual:,.2f}",
            annotation_position="bottom right",
            annotation_font=dict(size=10, color=GUINDA)
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

        # Construcción de la tabla ordenada por mes con encabezado fijo (sticky header) y diseño acorde al archivo
        rows_tabla_meses = []
        for i, (_, r_m) in enumerate(df_meses.iterrows()):
            mes_nombre = str(r_m[col_mes]).capitalize()
            monto_mes = r_m[col_recurso]
            bg_row = CARD if i % 2 == 0 else "#FAF8F5"
            rows_tabla_meses.append(
                html.Tr([
                    html.Td(mes_nombre, style={"padding": "9px 12px", "borderBottom": f"1px solid {LINE}", "fontSize": "11.5px", "color": INK}),
                    html.Td(f"${monto_mes:,.2f}", style={"padding": "9px 12px", "borderBottom": f"1px solid {LINE}", "fontSize": "11.5px", "textAlign": "right", "fontWeight": "600", "color": INK})
                ], style={"backgroundColor": bg_row})
            )

        # Fila de promedio / total general
        rows_tabla_meses.append(
            html.Tr([
                html.Td("Promedio mensual", style={"padding": "10px 12px", "fontWeight": "700", "fontSize": "12px", "color": GUINDA_DARK, "background": GUINDA_LIGHT, "borderTop": f"2px solid {GUINDA}"}),
                html.Td(f"${promedio_mensual:,.2f}", style={"padding": "10px 12px", "fontWeight": "700", "fontSize": "12px", "textAlign": "right", "color": GUINDA_DARK, "background": GUINDA_LIGHT, "borderTop": f"2px solid {GUINDA}"})
            ])
        )

        tabla_meses_componente = html.Div([
            html.Div("Detalle por Mes y Promedio", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em", "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"}),
            html.Div(
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Mes", style={
                            "padding": "9px 12px", "background": BG, "borderBottom": f"2px solid {LINE}", 
                            "fontSize": "11px", "color": INK_SOFT, "position": "sticky", "top": "0", "zIndex": "2", "textTransform": "uppercase", "letterSpacing": ".03em"
                        }),
                        html.Th("Recurso", style={
                            "padding": "9px 12px", "background": BG, "borderBottom": f"2px solid {LINE}", 
                            "fontSize": "11px", "textAlign": "right", "color": INK_SOFT, "position": "sticky", "top": "0", "zIndex": "2", "textTransform": "uppercase", "letterSpacing": ".03em"
                        })
                    ])),
                    html.Tbody(rows_tabla_meses)
                ], style={"width": "100%", "borderCollapse": "collapse"}),
                style={"maxHeight": "290px", "overflowY": "auto", "border": f"1px solid {LINE}", "borderRadius": "6px", "background": CARD, "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.02)"}
            )
        ])

        grafica_y_tabla_row = dbc.Row([
            dbc.Col(_chart_panel("Histórico mensual y línea de promedio de entrega de recursos", fig_linea, color_top=VERDE), md=8, className="mb-3"),
            dbc.Col(tabla_meses_componente, md=4, className="mb-3"),
        ])

        # Tarjetas inferiores — Desglose por rubro (filtradas sin ceros)
        tarjetas_rubros_cols = []
        for i, (_, row) in enumerate(df_rubros.iterrows()):
            nombre_rubro = str(row[col_rubro])
            pct_inv = row['PORCENTAJE_INV']
            ben_rubro = row[col_beneficiarios]
            pct_ben = row['PORCENTAJE_BEN']
            color_tarjeta = GUINDA if i % 2 == 0 else VERDE

            tarjetas_rubros_cols.append(
                dbc.Col(_rubro_card(nombre_rubro, pct_inv, ben_rubro, pct_ben, color_tarjeta),
                        width=12, sm=6, md=3, className="mb-3")
            )

        grid_tarjetas_rubros = dbc.Row(tarjetas_rubros_cols)

        # Layout consolidado final
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general de apoyos"),
            kpis_row,
            _section_label("ti-chart-area", "Comportamiento e histórico"),
            grafica_y_tabla_row,
            _section_label("ti-list-details", "Desglose porcentual y poblacional por rubro"),
            grid_tarjetas_rubros,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Recepción / Rendición de Cuentas: {str(e)}", color="danger", className="m-3")