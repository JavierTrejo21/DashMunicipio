# areas/desayunos_escolares.py
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, callback, Input, Output

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

# Variable global interna para mantener el DataFrame limpio disponible para el callback
_df_desayunos_cache = None


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


def _chart_panel(titulo, fig, color_top=GUINDA):
    return html.Div([
        html.Div(titulo, style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
                                 "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"}),
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True}, style={"width": "100%"}),
    ], style={"background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
               "borderTop": f"3px solid {color_top}", "padding": "16px 18px 8px", "overflow": "hidden"})


def analizar_desayunos_escolares(df):
    """Análisis estructurado para DIF Desayunos Escolares con enfoque institucional, tarjeta de beneficiarios en guinda y tabla filtrable."""
    global _df_desayunos_cache

    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Desayunos Escolares no contiene registros válidos.", color="danger", className="m-3")

    df_clean = df.copy()
    df_clean.columns = [str(c).strip() for c in df_clean.columns]

    # Mapeo exacto de columnas
    col_mes = next((c for c in df_clean.columns if "MES" in c.upper()), "Mes")
    col_comunidad = next((c for c in df_clean.columns if "COMUNIDAD" in c.upper()), "Comunidad")
    col_beneficiarios = next((c for c in df_clean.columns if "BENEFICIARIO" in c.upper()), "Beneficiarios")
    col_escuelas = next((c for c in df_clean.columns if "ESCUELA" in c.upper()), "Escuelas beneficiadas")
    col_cantidad = next((c for c in df_clean.columns if "CANTIDAD" in c.upper() or "TOTAL" in c.upper()), "Cantidad")
    col_actividad = next((c for c in df_clean.columns if "ACTIVIDAD" in c.upper() or "CONCEPTO" in c.upper()), "Actividad")

    # Limpieza y normalización
    df_limpio = pd.DataFrame()
    df_limpio['Mes'] = df_clean[col_mes].astype(str).str.strip().str.capitalize()
    df_limpio['Comunidad'] = df_clean[col_comunidad].astype(str).str.strip().str.title()
    df_limpio['Beneficiarios'] = pd.to_numeric(df_clean[col_beneficiarios], errors='coerce').fillna(0)
    df_limpio['Escuelas'] = pd.to_numeric(df_clean[col_escuelas], errors='coerce').fillna(0)
    df_limpio['Cantidad'] = pd.to_numeric(df_clean[col_cantidad], errors='coerce').fillna(0)
    df_limpio['Actividad'] = df_clean[col_actividad].astype(str).str.strip().str.title()

    # Guardamos en caché para el callback
    _df_desayunos_cache = df_limpio.copy()

    # Métricas globales
    total_desayunos = df_limpio['Cantidad'].sum()

    # Cálculo exacto de Beneficiarios (Máximo por comunidad y mes, luego suma de máximos)
    df_benef_mes = df_limpio.groupby(['Comunidad', 'Mes'], as_index=False)['Beneficiarios'].max()
    max_benef_por_comunidad = df_benef_mes.groupby('Comunidad')['Beneficiarios'].max()
    total_beneficiarios = int(max_benef_por_comunidad.sum())

    # Cálculo exacto de Escuelas (Máximo por comunidad y mes, luego suma de máximos)
    df_escuelas_mes = df_limpio.groupby(['Comunidad', 'Mes'], as_index=False)['Escuelas'].max()
    max_escuelas_por_comunidad = df_escuelas_mes.groupby('Comunidad')['Escuelas'].max()
    total_escuelas_acumulado = int(max_escuelas_por_comunidad.sum())

    comunidades_disponibles = sorted(df_limpio['Comunidad'].unique())

    # =================================================================
    # TARJETA DE ENFOQUE DEL MÓDULO
    # =================================================================
    enfoque_card = html.Div([
        html.Div([
            html.I(className="ti ti-info-circle", style={"fontSize": "15px", "color": VERDE}),
            html.Span("Enfoque del programa de desayunos escolares", style={
                "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "13px",
                "letterSpacing": ".04em", "color": GUINDA_DARK, "textTransform": "uppercase"
            }),
        ], style={"display": "flex", "alignItems": "center", "gap": "8px",
                  "borderBottom": f"1px solid {LINE}", "paddingBottom": "10px", "marginBottom": "12px"}),
        html.P(
            "El programa opera mediante la entrega permanente de desayunos fríos y calientes destinados a más de 118 escuelas en el municipio y más de 2,114 alumnos, asegurando una nutrición infantil adecuada y el rendimiento escolar.",
            style={"fontSize": "12.5px", "color": INK_SOFT, "lineHeight": "1.6", "marginBottom": "10px"}
        ),
        html.Ul([
            html.Li("Operación continua de modalidades en desayunos escolares fríos y calientes.",
                    style={"fontSize": "12px", "color": INK, "marginBottom": "6px"}),
            html.Li("Control geográfico y seguimiento operativo enfocado en más de 118 escuelas del municipio.",
                    style={"fontSize": "12px", "color": INK, "marginBottom": "6px"}),
            html.Li(f"Volumen general acumulado en el periodo: {int(total_desayunos):,} porciones entregadas a más de 2,114 alumnos.",
                    style={"fontSize": "12px", "color": INK, "fontWeight": "600"}),
        ], style={"paddingLeft": "18px", "margin": "0"}),
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {VERDE}", "padding": "16px 20px",
        "boxShadow": "0 1px 2px rgba(84,19,42,.05)"
    })

    # =================================================================
    # KPI CARDS (estilo institucional: badge-ring + borde superior)
    # =================================================================
    kpis_row = dbc.Row([
        dbc.Col(_kpi_card("ti-bowl", "Total de porciones", f"{int(total_desayunos):,} porciones", "Volumen acumulado del periodo", VERDE), width=12, md=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-users", "Beneficiarios atendidos", f"{int(total_beneficiarios):,} alumnos", "Matrícula beneficiada", GUINDA), width=12, md=4, className="mb-3"),
        dbc.Col(_kpi_card("ti-school", "Escuelas beneficiadas", f"{total_escuelas_acumulado:,} escuelas", "Cobertura municipal", VERDE), width=12, md=4, className="mb-3"),
    ])

    # =================================================================
    # GRÁFICA HISTÓRICA (LÍNEA)
    # =================================================================
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df_meses = df_limpio.groupby('Mes', as_index=False)['Cantidad'].sum()
    df_meses['Mes_Ord'] = pd.Categorical(df_meses['Mes'], categories=orden_meses, ordered=True)
    df_meses = df_meses.sort_values('Mes_Ord').dropna(subset=['Mes_Ord'])

    fig_lineas = go.Figure()
    fig_lineas.add_trace(go.Scatter(
        x=df_meses['Mes'], y=df_meses['Cantidad'],
        mode='lines+markers+text',
        name='Porciones',
        line=dict(color=GUINDA, width=3),
        marker=dict(size=8, color=VERDE),
        text=df_meses['Cantidad'].apply(lambda x: f"{int(x):,}"),
        textposition="top center",
        textfont=dict(family="Inter, sans-serif", size=10, color=INK_SOFT)
    ))
    fig_lineas.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=30, l=40, r=40), height=300,
        xaxis=dict(showgrid=True, gridcolor=LINE, tickangle=0, tickfont=dict(color=INK_SOFT, family="Inter, sans-serif")),
        yaxis=dict(showgrid=True, gridcolor=LINE, rangemode='tozero', tickfont=dict(color=INK_SOFT, family="Inter, sans-serif")),
        showlegend=False,
        font=dict(family="Inter, sans-serif")
    )

    seccion_grafica = _chart_panel("Histórico de entrega de porciones por mes", fig_lineas, color_top=GUINDA)

    # =================================================================
    # TABLA INTERACTIVA CON FILTRO POR COMUNIDAD
    # =================================================================
    df_tabla_inicial = df_limpio[['Comunidad', 'Mes', 'Actividad', 'Escuelas', 'Beneficiarios', 'Cantidad']].copy()
    df_tabla_inicial.columns = ['Comunidad', 'Mes', 'Modalidad', 'Escuelas', 'Beneficiarios', 'Porciones']

    tabla_detallada = dash_table.DataTable(
        id='tabla-comunidades-desayunos',
        data=df_tabla_inicial.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_tabla_inicial.columns],
        page_size=8,
        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': '320px',
        },
        style_header={
            'backgroundColor': GUINDA_DARK,
            'color': '#ffffff',
            'fontWeight': '700',
            'textAlign': 'center',
            'fontSize': '10.5px',
            'letterSpacing': '.04em',
            'textTransform': 'uppercase',
            'border': 'none',
            'fontFamily': 'Inter, sans-serif',
            'padding': '10px 14px',
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px 14px',
            'fontSize': '12px',
            'fontFamily': 'Inter, sans-serif',
            'color': INK,
            'borderBottom': f'1px solid {LINE}',
            'backgroundColor': CARD,
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#FAF8F4'},
        ],
        sort_action='native'
    )

    filtro_seccion = html.Div([
        # Dropdown de filtro
        html.Div([
            html.Div([
                html.I(className="ti ti-filter", style={"color": VERDE, "fontSize": "15px"}),
                html.Span("Consulta detallada por comunidad", style={
                    "fontFamily": FONT_SERIF, "fontWeight": "700", "fontSize": "13px",
                    "letterSpacing": ".04em", "color": GUINDA_DARK, "textTransform": "uppercase"
                }),
            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}),
            html.P(
                "Selecciona o busca una comunidad para verificar el detalle de las escuelas beneficiadas, alumnos y porciones entregadas:",
                style={"fontSize": "12px", "color": INK_SOFT, "marginBottom": "10px"}
            ),
            dcc.Dropdown(
                id='dropdown-filtro-comunidad-desayunos',
                options=[{'label': c, 'value': c} for c in comunidades_disponibles],
                placeholder="Selecciona una comunidad (muestra todos si está vacío)...",
                clearable=True,
                style={"fontSize": "13px", "fontFamily": FONT_SANS}
            ),
        ], style={
            "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
            "borderTop": f"3px solid {VERDE}", "padding": "16px 18px", "marginBottom": "12px"
        }),
        # Tabla filtrable
        html.Div(
            tabla_detallada,
            style={
                "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
                "borderTop": f"3px solid {GUINDA}", "overflow": "hidden"
            }
        ),
    ])

    # =================================================================
    # LAYOUT CONSOLIDADO FINAL
    # =================================================================
    return html.Div([
        _fuentes_e_iconos(),
        _section_label("ti-info-circle", "Enfoque del programa"),
        enfoque_card,
        _section_label("ti-chart-bar", "Resumen general"),
        kpis_row,
        _section_label("ti-chart-line", "Tendencia mensual"),
        seccion_grafica,
        _section_label("ti-map-pin", "Detalle por comunidad"),
        filtro_seccion,
    ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})


# --- CALLBACK PARA FILTRAR LA TABLA EN TIEMPO REAL ---
@callback(
    Output('tabla-comunidades-desayunos', 'data'),
    Input('dropdown-filtro-comunidad-desayunos', 'value')
)
def filtrar_tabla_comunidad(comunidad_seleccionada):
    global _df_desayunos_cache
    if _df_desayunos_cache is None or _df_desayunos_cache.empty:
        return []

    df_tabla = _df_desayunos_cache[['Comunidad', 'Mes', 'Actividad', 'Escuelas', 'Beneficiarios', 'Cantidad']].copy()
    df_tabla.columns = ['Comunidad', 'Mes', 'Modalidad', 'Escuelas', 'Beneficiarios', 'Porciones']

    if comunidad_seleccionada:
        df_tabla = df_tabla[df_tabla['Comunidad'] == comunidad_seleccionada]

    return df_tabla.to_dict('records')