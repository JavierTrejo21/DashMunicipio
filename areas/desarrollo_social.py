# areas/desarrollo_social.py
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA (misma que los demás módulos)
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
# BLOQUES DE LAYOUT (idénticos a los usados en los demás módulos)
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
                html.Div(valor, style={"fontWeight": "700", "fontSize": "16px", "lineHeight": "1.25", "color": INK, "wordBreak": "break-word"}),
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
               "borderTop": f"3px solid {color_top}", "padding": "16px 18px 12px", "overflow": "hidden", "height": "100%",
               "boxSizing": "border-box"})


def analizar_desarrollo_social(df):
    """
    Módulo analítico — Dirección de Desarrollo Social.
    Misma estructura visual y colorimetría institucional (guinda/verde) que
    los demás módulos del sistema; la lógica analítica no cambia.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Desarrollo Social no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_soc = df.copy()
    df_soc.columns = [str(c).strip().upper() for c in df_soc.columns]
    columnas_reales = df_soc.columns.tolist()

    col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
    col_benef = next((c for c in columnas_reales if "BENEF" in c), "BENEFICIARIOS")
    col_act = next((c for c in columnas_reales if "ACT" in c), "ACTIVIDAD")
    col_var = next((c for c in columnas_reales if "VAR" in c), "VARIABLE")
    col_con = next((c for c in columnas_reales if "CON" in c), "CONCEPTO")
    col_com = next((c for c in columnas_reales if "COMUNIDAD" in c), "COMUNIDAD")

    # --- LIMPIEZA RIGUROSA Y ESTANDARIZACIÓN TEXTUAL ---
    df_soc[col_benef] = pd.to_numeric(df_soc[col_benef], errors='coerce').fillna(0).astype(int)
    df_soc[col_var] = df_soc[col_var].fillna("PENDIENTE DE APROBACIÓN").astype(str).str.strip().str.upper()
    df_soc[col_act] = df_soc[col_act].fillna("OTROS APOYOS").astype(str).str.strip().str.upper()
    df_soc[col_com] = df_soc[col_com].fillna("SIN ESPECIFICAR").astype(str).str.strip().str.upper()

    # --- CÁLCULO DE INDICADORES (KPIs) ---
    total_beneficiarios = int(df_soc[col_benef].sum())
    total_expedientes = len(df_soc)

    df_top_com = df_soc.groupby(col_com)[col_benef].sum().reset_index(name='TOTAL_APOYOS')
    if not df_top_com.empty and df_top_com['TOTAL_APOYOS'].sum() > 0:
        idx_max = df_top_com['TOTAL_APOYOS'].idxmax()
        comunidad_lider = df_top_com.loc[idx_max, col_com]
        apoyos_lider = df_top_com.loc[idx_max, 'TOTAL_APOYOS']
        texto_comunidad = f"{comunidad_lider} ({int(apoyos_lider)} u.)"
    else:
        texto_comunidad = df_soc[col_com].value_counts().index[0] if not df_soc.empty else "Por definir"

    pendientes = int(df_soc[df_soc[col_var].str.contains("PENDIENTE", na=False)].shape[0])
    realizados = total_expedientes - pendientes
    porcentaje_eficacia = (realizados / total_expedientes * 100) if total_expedientes > 0 else 0

    # --- TARJETAS KPI (estilo institucional: badge-ring + borde superior) ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(_kpi_card("ti-users", "Ciudadanos beneficiados", f"{total_beneficiarios:,.0f} habs.", "Impacto social acumulado", VERDE), width=12, sm=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-map-pin", "Zona de mayor atención territorial", texto_comunidad, "Localidad con más apoyos dispersados", GUINDA), width=12, sm=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-alert-triangle", "Expedientes pendientes de aprobación", f"{pendientes} casos", "Requieren validación o desahogo", GUINDA), width=12, sm=4, className="mb-3"),
    ])

    # --- GRÁFICA 1: ANILLO DE DISTRIBUCIÓN POR PROGRAMA ---
    df_prog = df_soc.groupby(col_act).size().reset_index(name='CONTEO')
    df_prog = df_prog.sort_values(by='CONTEO', ascending=False).reset_index(drop=True)

    fig_programas = go.Figure(data=[go.Pie(
        labels=df_prog[col_act],
        values=df_prog['CONTEO'],
        hole=0.6,
        textinfo='percent',
        textposition='inside',
        insidetextfont=dict(color='white', size=11, family="Inter, sans-serif"),
        marker=dict(colors=[GUINDA, VERDE, "#C9A0AE", INK_FAINT, LINE], line=dict(color="#fff", width=1)),
        hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )])

    fig_programas.update_layout(
        annotations=[dict(text=f"<b>{total_expedientes}</b><br>Total", x=0.5, y=0.5, font_size=13, font_color=INK, showarrow=False)],
        margin=dict(l=10, r=130, t=10, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=9, color=INK, family="Inter")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280
    )
    panel_programas = _chart_panel(
        "Distribución por programa social",
        dcc.Graph(figure=fig_programas, config={'displayModeBar': False}),
        color_top=VERDE
    )

    # --- GRÁFICA 2: INDICADOR RADIAL DE EFICACIA ---
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=porcentaje_eficacia,
        number=dict(suffix="%", font=dict(color=VERDE_DARK, size=26, family="Inter, sans-serif")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor=INK_SOFT),
            bar=dict(color=VERDE),
            bgcolor="white",
            borderwidth=2,
            bordercolor=LINE,
            steps=[
                dict(range=[0, 50], color=BG),
                dict(range=[50, 80], color="#E7E3D8"),
                dict(range=[80, 100], color=VERDE_LIGHT)
            ],
            threshold=dict(line=dict(color=GUINDA, width=4), thickness=0.75, value=porcentaje_eficacia)
        )
    ))
    fig_gauge.update_layout(margin=dict(l=20, r=20, t=20, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=240)

    panel_gauge = _chart_panel(
        "Eficacia global de gestión",
        html.Div([
            html.P("Porcentaje consolidado de expedientes concluidos vs. meta institucional.",
                   className="text-center mb-1", style={"fontSize": "0.68rem", "color": INK_SOFT, "fontWeight": "500"}),
            dcc.Graph(figure=fig_gauge, config={'displayModeBar': False})
        ]),
        color_top=GUINDA
    )

    # --- TABLA DE HISTORIAL DETALLADO (estilo institucional) ---
    columnas_tabla = [
        {"name": "Mes", "id": col_mes},
        {"name": "Localidad", "id": col_com},
        {"name": "Estatus (Variable)", "id": col_var},
        {"name": "Acción Operativa / Actividad", "id": col_act},
        {"name": "Beneficiarios", "id": col_benef}
    ]

    tabla_historial = html.Div([
        dash_table.DataTable(
            data=df_soc.to_dict('records'),
            columns=columnas_tabla,
            page_size=6,
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': GUINDA_DARK, 'color': 'white', 'fontWeight': '700',
                'fontSize': '10.5px', 'letterSpacing': '.04em', 'textTransform': 'uppercase',
                'textAlign': 'left', 'padding': '10px 14px', 'border': 'none'
            },
            style_cell={'padding': '9px 14px', 'fontSize': '12.5px', 'fontFamily': 'Inter, sans-serif',
                        'textAlign': 'left', 'color': INK, 'border': 'none', 'borderBottom': f'1px solid {LINE}'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#FAF8F4'}],
            style_as_list_view=True,
        )
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {VERDE}", "overflow": "hidden", "padding": "8px"})

    # --- CONSTRUCCIÓN DEL LAYOUT FINAL ---
    layout_final = html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-chart-bar", "Resumen general"),
        tarjetas_kpi,

        _section_label("ti-chart-donut", "Programas y eficacia"),
        dbc.Row([
            dbc.Col(panel_programas, md=6, className="mb-3"),
            dbc.Col(panel_gauge, md=6, className="mb-3"),
        ]),

        _section_label("ti-table", "Padrón general e histórico de apoyos directos"),
        dbc.Row([dbc.Col(tabla_historial, md=12)]),
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    return layout_final