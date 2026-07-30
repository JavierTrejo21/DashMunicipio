# areas/mujeres.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def analizar_instancia_mujeres(df):
    """
    Módulo analítico premium para la Instancia Municipal de las Mujeres.
    Diseño horizontal compacto para las líneas de acción secundarias.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de la Instancia de las Mujeres no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_muj = df.copy()
    df_muj.columns = [str(c).strip().upper() for c in df_muj.columns]
    columnas_reales = df_muj.columns.tolist()

    # Identificación tolerante de columnas originales
    col_num = next((c for c in columnas_reales if "NUM" in c), "NUMERO")
    col_act = next((c for c in columnas_reales if "ACT" in c), "ACTIVIDAD")
    col_atn = next((c for c in columnas_reales if "ATEN" in c or "ATEND" in c), "ATENDIDOS")
    col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
    col_var = next((c for c in columnas_reales if "VAR" in c), "VARIABLE")
    col_inv = next((c for c in columnas_reales if "INV" in c), "INVERSION")

    # --- LIMPIEZA RIGUROSA ---
    df_muj[col_atn] = pd.to_numeric(df_muj[col_atn], errors='coerce').fillna(0).astype(int)
    df_muj[col_inv] = pd.to_numeric(df_muj[col_inv], errors='coerce').fillna(0)
    df_muj[col_var] = df_muj[col_var].fillna("OTRAS ACCIONES").astype(str).str.strip().str.upper()
    df_muj[col_act] = df_muj[col_act].fillna("SIN ESPECIFICAR").astype(str).str.strip()
    df_muj[col_mes] = df_muj[col_mes].fillna("S/M").astype(str).str.strip().str.upper()

    # --- CÁLCULO DE INDICADORES (KPIs) ---
    total_atendidos = int(df_muj[col_atn].sum())
    total_inversion = df_muj[col_inv].sum()
    
    df_canalizaciones = df_muj[df_muj[col_var].str.contains("CANALIZA", na=False)]
    total_canalizados = int(df_canalizaciones[col_atn].sum()) if not df_canalizaciones.empty else 0

    # --- TARJETAS SUPERIORES ESTILO INFOGRÁFICO ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#691c32", "borderRadius": "8px 0 0 8px"}),
                html.Small("MUJERES Y PERSONAS ATENDIDAS", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"{total_atendidos:,.0f} Benef.", className="m-0 font-weight-bold mt-1", style={"color": "#691c32", "fontSize": "1.2rem"}),
                html.Small("Alcance acumulado en actividades y talleres", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#115e59", "borderRadius": "8px 0 0 8px"}),
                html.Small("CASOS CANALIZADOS A OTRAS INSTANCIAS", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"{total_canalizados} Casos", className="m-0 font-weight-bold mt-1", style={"color": "#115e59", "fontSize": "1.2rem"}),
                html.Small("Protección, seguimiento y vinculación segura", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#bc955c", "borderRadius": "8px 0 0 8px"}),
                html.Small("INVERSIÓN SOCIAL DIRECTA", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"${total_inversion:,.2f}", className="m-0 font-weight-bold mt-1", style={"color": "#bc955c", "fontSize": "1.2rem"}),
                html.Small("Fondo asignado a talleres y apoyos", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
    ], className="mb-2")

    # --- GENERACIÓN DE MINI-TARJETAS HORIZONTALES (BADGES DE ACCIÓN) ---
    df_var_filtrado = df_muj[~df_muj[col_var].str.contains("MUJERES BENEFICIARIAS", na=False)]
    df_var_agrupado = df_var_filtrado.groupby(col_var)[col_atn].sum().reset_index(name='TOTAL_ATENDIDOS')
    
    colores_badges = ["#115e59", "#bc955c", "#691c32", "#2563eb", "#d97706", "#4b5563"]
    
    badges_items = []
    for i, row in df_var_agrupado.iterrows():
        color_actual = colores_badges[i % len(colores_badges)]
        badges_items.append(
            html.Div([
                html.Div([
                    html.I(className="bi bi-circle-fill me-1", style={"fontSize": "0.5rem", "color": color_actual})
                ], className="d-flex align-items-center mb-1"),
                html.H4(f"{row['TOTAL_ATENDIDOS']:,}", className="font-weight-bold m-0", style={"color": color_actual, "fontSize": "1.1rem"}),
                html.Small(row[col_var].title(), className="d-block text-muted font-weight-bold mt-1", style={"fontSize": "0.65rem", "lineHeight": "1.1"})
            ], style={
                "minWidth": "115px", 
                "flex": "1", 
                "backgroundColor": "#ffffff", 
                "border": "1px solid #e5e7eb", 
                "borderTop": f"3px solid {color_actual}",
                "borderRadius": "6px", 
                "padding": "10px 8px", 
                "textAlign": "center",
                "boxShadow": "0 1px 2px rgba(0,0,0,0.05)"
            })
        )

    panel_horizontal = html.Div(
        badges_items, 
        style={
            "display": "flex", 
            "flexDirection": "row", 
            "gap": "8px", 
            "overflowX": "auto", 
            "paddingBottom": "5px",
            "alignItems": "stretch"
        }
    )

    # --- GRÁFICA 2: COMPORTAMIENTO TEMPORAL (BARRAS MENSUALES ESTILIZADAS) ---
    df_mes_agrupado = df_muj.groupby(col_mes)[col_atn].sum().reset_index(name='TOTAL_MES')
    meses_orden = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    df_mes_agrupado[col_mes] = pd.Categorical(df_mes_agrupado[col_mes], categories=meses_orden, ordered=True)
    df_mes_agrupado = df_mes_agrupado.sort_values(col_mes).dropna()

    fig_temporal = px.bar(
        df_mes_agrupado, x=col_mes, y='TOTAL_MES',
        color_discrete_sequence=["#bc955c"]
    )
    fig_temporal.update_layout(
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis=dict(title=None, tickfont=dict(size=10, color="#1f2937"), gridcolor="#f3f4f6"),
        yaxis=dict(title=None, tickfont=dict(size=10, color="#1f2937"), gridcolor="#f3f4f6"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=280
    )

    # --- TABLA DE HISTORIAL DETALLADO ---
    df_muj["INVERSION_M"] = df_muj[col_inv].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")
    
    columnas_tabla = [
        {"name": "Eje Estratégico", "id": col_var},
        {"name": "Actividad Impartida / Registro", "id": col_act},
        {"name": "Mes", "id": col_mes},
        {"name": "Personas Atendidas", "id": col_atn},
        {"name": "Inversión Aplicada", "id": "INVERSION_M"}
    ]

    estilos_animacion = dcc.Markdown("""
    <style>
        @keyframes fadeInSlide {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .animar-entrada {
            animation: fadeInSlide 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
    </style>
    """, dangerously_allow_html=True)

    # --- LAYOUT FINAL ---
    return html.Div([
        estilos_animacion,
        tarjetas_kpi,
        
        # Bloque de Visualizaciones con el Panel Horizontal de Líneas de Acción
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-collection-fill me-2"), "RESUMEN DE LÍNEAS DE ACCIÓN OPERATIVA"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Desglose dinámico de indicadores por programa secundario.", 
                           className="text-center mb-3", 
                           style={"fontSize": "0.68rem", "color": "#1f2937", "fontWeight": "500"}),
                    panel_horizontal
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px", "display": "flex", "flexDirection": "column", "justifyContent": "center"})
            ], className="shadow-sm mb-4 animar-entrada"), md=6),
            
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-graph-up me-2"), "COMPORTAMIENTO TEMPORAL: IMPACTO MENSUAL DE ATENCIONES"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Volumen histórico de personas beneficiadas por periodo mensual.", 
                           className="text-center mb-1", 
                           style={"fontSize": "0.68rem", "color": "#1f2937", "fontWeight": "500"}),
                    dcc.Graph(figure=fig_temporal, config={'displayModeBar': False})
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=6),
        ]),

        # Bloque de la Tabla Histórica
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    html.I(className="bi bi-gender-female me-2", style={"color": "#bc955c"}),
                    "REGISTRO OPERATIVO Y METAS HISTÓRICAS - INSTANCIA DE LAS MUJERES"
                ], style={
                    'backgroundColor': '#691c32', 'color': 'white', 'padding': '12px 16px', 
                    'fontWeight': '700', 'fontSize': '0.8rem', 'borderRadius': '6px 6px 0 0'
                }),
                html.Div([
                    dash_table.DataTable(
                        data=df_muj.to_dict('records'),
                        columns=columnas_tabla,
                        page_size=6,
                        style_table={'overflowX': 'auto'},
                        style_header={'backgroundColor': '#f3f4f6', 'color': '#1f2937', 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'},
                        style_cell={'padding': '9px 8px', 'fontSize': '11px', 'fontFamily': 'sans-serif', 'textAlign': 'left', 'borderBottom': '1px solid #f3f4f6'},
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}]
                    )
                ], className="bg-white border border-top-0 p-2", style={'borderRadius': '0 0 6px 6px'})
            ], className="shadow-sm mb-2 animar-entrada"), md=12)
        ])
    ], style={'padding': '5px'})