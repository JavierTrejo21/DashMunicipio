# areas/orientacion_alimentaria.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc

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

# Paleta combinada para el anillo (institucional)
COLORES_ANILLO = [VERDE, GUINDA, "#bc955c", "#2b6cb0", INK_SOFT]


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


def _panel(titulo, contenido, color_top=GUINDA):
    """Panel con encabezado de color institucional y contenido libre."""
    return html.Div([
        html.Div(titulo, style={
            "fontSize": "11px", "fontWeight": "700", "letterSpacing": ".03em",
            "textTransform": "uppercase", "color": INK_SOFT, "marginBottom": "10px"
        }),
        contenido,
    ], style={
        "background": CARD, "border": f"1px solid {LINE}", "borderRadius": "8px",
        "borderTop": f"3px solid {color_top}", "padding": "16px 18px 12px",
        "overflow": "hidden", "height": "100%", "boxSizing": "border-box"
    })


def analizar_orientacion_alimentaria(df):
    """
    Módulo Operativo para Orientación y Educación Alimentaria (DIF).
    - Incluye gráfica de anillo infográfico con total centralizado.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Orientación Alimentaria llegó vacío.", color="warning", className="m-3")

    try:
        # 1. Copiar y normalizar nombres de columnas
        df_alim = df.copy()
        df_alim.columns = [str(c).strip().upper() for c in df_alim.columns]

        col_actividad = next((c for c in df_alim.columns if "ACTIVIDAD" in c), None)
        col_beneficiarios = next((c for c in df_alim.columns if "BENEFICIARIO" in c or "CANTIDAD" in c), None)
        col_institucion = next((c for c in df_alim.columns if "INSTITUCION" in c or "INSTITUCIÓN" in c), None)

        if col_beneficiarios:
            df_alim[col_beneficiarios] = pd.to_numeric(df_alim[col_beneficiarios], errors='coerce').fillna(0)
            col_cantidad_sistema = col_beneficiarios
        else:
            df_alim["BENEF_GENERICO"] = 0
            col_cantidad_sistema = "BENEF_GENERICO"

        if col_actividad: df_alim[col_actividad] = df_alim[col_actividad].astype(str).str.strip().str.title()
        if col_institucion: df_alim[col_institucion] = df_alim[col_institucion].astype(str).str.strip().str.title()

        df_activos = df_alim[df_alim[col_cantidad_sistema] > 0].copy()

        # =================================================================
        # 2. MÉTRICAS SUPERIORES (KPIs)
        # =================================================================
        total_orientados = df_activos[col_cantidad_sistema].sum()
        total_temas = df_activos[col_actividad].nunique()

        kpis_row = dbc.Row([
            dbc.Col(_kpi_card("ti-users", "Ciudadanos orientados", f"{int(total_orientados):,} personas", "Periodo actual", VERDE), width=12, sm=6, className="mb-3"),
            dbc.Col(_kpi_card("ti-school", "Temas formativos desarrollados", f"{total_temas} talleres eje", "Actividades registradas", GUINDA), width=12, sm=6, className="mb-3"),
        ])

        # =================================================================
        # 3. ANILLO INFOGRÁFICO CON TOTAL CENTRALIZADO
        # =================================================================
        df_inst = df_activos.groupby(col_institucion)[col_cantidad_sistema].sum().reset_index()

        fig_donut = px.pie(
            df_inst, values=col_cantidad_sistema, names=col_institucion,
            hole=0.6,
            color_discrete_sequence=COLORES_ANILLO
        )
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent',
            textfont=dict(size=11, family="Inter, sans-serif", color="white"),
            marker=dict(line=dict(color='#ffffff', width=2)),
            hovertemplate="<b>%{label}</b><br>Atendidos: %{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>"
        )
        fig_donut.add_annotation(
            text=f"<b>{int(total_orientados):,}</b><br><span style='font-size:10px; color:{INK_SOFT};'>Total</span>",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color=INK, family="Inter, sans-serif")
        )
        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5,
                xanchor="left", x=1.02,
                font=dict(size=10, color=INK_SOFT, family="Inter, sans-serif")
            ),
            height=260,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )

        # =================================================================
        # 4. TABLA DE TEMAS (con scroll vertical)
        # =================================================================
        df_temas = df_activos.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_temas = df_temas.sort_values(by=col_cantidad_sistema, ascending=False)
        df_temas['CANTIDAD_FORMATO'] = df_temas[col_cantidad_sistema].apply(lambda x: f"{x:,.0f}")

        tabla_ejecutiva = dash_table.DataTable(
            data=df_temas.to_dict('records'),
            columns=[
                {"name": "Temática del Taller Impartido", "id": col_actividad},
                {"name": "Beneficiarios", "id": "CANTIDAD_FORMATO"}
            ],
            style_as_list_view=True,
            style_header={
                'backgroundColor': GUINDA_DARK,
                'fontWeight': '700',
                'color': '#ffffff',
                'fontSize': '10.5px',
                'letterSpacing': '.04em',
                'textTransform': 'uppercase',
                'borderBottom': f'2px solid {LINE}',
                'padding': '10px 14px',
                'fontFamily': 'Inter, sans-serif',
            },
            style_cell={
                'padding': '10px 14px',
                'fontSize': '12px',
                'color': INK,
                'fontFamily': 'Inter, sans-serif',
                'borderBottom': f'1px solid {LINE}',
                'backgroundColor': CARD,
            },
            style_cell_conditional=[
                {'if': {'column_id': col_actividad}, 'textAlign': 'left', 'fontWeight': '600'},
                {'if': {'column_id': 'CANTIDAD_FORMATO'}, 'textAlign': 'center', 'fontWeight': '700', 'color': GUINDA_DARK},
            ],
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#FAF8F4'},
            ],
            style_table={
                'maxHeight': '240px',
                'overflowY': 'auto',
            }
        )

        # =================================================================
        # 5. MAQUETACIÓN: ANILLO (IZQ) + TABLA (DER)
        # =================================================================
        bloque_dashboard = dbc.Row([
            dbc.Col(
                _panel(
                    "Distribución por nivel / entorno educativo",
                    dcc.Graph(figure=fig_donut, config={'displayModeBar': False}),
                    color_top=GUINDA
                ),
                width=12, lg=6, className="mb-3"
            ),
            dbc.Col(
                _panel(
                    "Alcance operativo detallado por taller",
                    tabla_ejecutiva,
                    color_top=VERDE
                ),
                width=12, lg=6, className="mb-3"
            ),
        ], className="g-3")

        # =================================================================
        # 6. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general"),
            kpis_row,
            _section_label("ti-layout-columns", "Distribución y alcance operativo"),
            bloque_dashboard,
        ], style={"background": BG, "fontFamily": FONT_SANS, "color": INK, "padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al procesar el módulo infográfico: {str(e)}", color="danger", className="m-3")