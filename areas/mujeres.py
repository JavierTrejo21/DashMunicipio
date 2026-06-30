# areas/mujeres.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def analizar_instancia_mujeres(df):
    """
    Módulo analítico premium para la Instancia Municipal de las Mujeres.
    Analiza alcances de atención, talleres, canalizaciones e inversión social.
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
    # 1. Total general de personas/mujeres atendidas en los registros
    total_atendidos = int(df_muj[col_atn].sum())
    
    # 2. Total de inversión registrada para programas de mujeres
    total_inversion = df_muj[col_inv].sum()
    
    # 3. Conteo específico de casos canalizados o atendidos en crisis de manera interna
    # Filtramos filas que mencionen canalizaciones o atención jurídica/psicológica si existen
    df_canalizaciones = df_muj[df_muj[col_var].str.contains("CANALIZA", na=False)]
    total_canalizados = int(df_canalizaciones[col_atn].sum()) if not df_canalizaciones.empty else 0

    # --- DISEÑO DE TARJETAS INSTITUCIONALES (KPIs) ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#691c32", "borderRadius": "8px 0 0 8px"}),
                html.Small("MUJERES Y PERSONAS ATENDIDAS", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{total_atendidos:,.0f} Benef.", className="m-0 font-weight-bold mt-1", style={"color": "#691c32", "fontSize": "1.3rem"}),
                html.Small("Alcance acumulado en actividades y talleres", className="text-muted d-block", style={"fontSize": "0.58rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#bc955c", "borderRadius": "8px 0 0 8px"}),
                html.Small("CASOS CANALIZADOS A OTRAS INSTANCIAS", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{total_canalizados} Casos", className="m-0 font-weight-bold mt-1", style={"color": "#1f2937", "fontSize": "1.3rem"}),
                html.Small("Protección, seguimiento y vinculación segura", className="text-muted d-block", style={"fontSize": "0.58rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#1f2937", "borderRadius": "8px 0 0 8px"}),
                html.Small("INVERSIÓN SOCIAL DIRECTA", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"${total_inversion:,.2f}", className="m-0 font-weight-bold mt-1", style={"color": "#bc955c", "fontSize": "1.3rem"}),
                html.Small("Fondo asignado a talleres y apoyos productivos", className="text-muted d-block", style={"fontSize": "0.58rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
    ], className="mb-2")

    # --- GRÁFICA 1: DONA - LÍNEAS DE ACCIÓN ESTRATÉGICA (VARIABLE) ---
    df_var_agrupado = df_muj.groupby(col_var)[col_atn].sum().reset_index(name='TOTAL_ATENDIDOS')
    df_var_agrupado[col_var] = df_var_agrupado[col_var].str.wrap(25)

    fig_variables = px.pie(
        df_var_agrupado, values='TOTAL_ATENDIDOS', names=col_var, hole=0.5,
        color_discrete_sequence=["#691c32", "#bc955c", "#1f2937", "#4b5563", "#9ca3af"]
    )
    fig_variables.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=8)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )

    # --- GRÁFICA 2: COMPORTAMIENTO TEMPORAL (ACCIONES POR MES) ---
    df_mes_agrupado = df_muj.groupby(col_mes)[col_atn].sum().reset_index(name='TOTAL_MES')
    
    # Ordenar los meses de forma lógica si es posible, o dejarlos por aparición
    meses_orden = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    df_mes_agrupado[col_mes] = pd.Categorical(df_mes_agrupado[col_mes], categories=meses_orden, ordered=True)
    df_mes_agrupado = df_mes_agrupado.sort_values(col_mes).dropna()

    fig_temporal = px.bar(
        df_mes_agrupado, x=col_mes, y='TOTAL_MES',
        color_discrete_sequence=["#bc955c"]
    )
    fig_temporal.update_layout(
        margin=dict(l=10, r=10, t=15, b=15),
        xaxis=dict(title=None, tickfont=dict(size=9)),
        yaxis=dict(title=dict(text="Personas Atendidas", font=dict(size=10)), gridcolor="#f3f4f6"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )

    # --- TABLA DE HISTORIAL DETALLADO ---
    columnas_tabla = [
        {"name": "Eje Estratégico", "id": col_var},
        {"name": "Actividad Impartida / Registro", "id": col_act},
        {"name": "Mes", "id": col_mes},
        {"name": "Personas Atendidas", "id": col_atn},
        {"name": "Inversión ($)", "id": col_inv}
    ]

    # --- CONSTRUCCIÓN DEL LAYOUT FINAL ---
    layout_final = html.Div([
        tarjetas_kpi,
        
        # Grid de Visualizaciones
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-pie-chart-fill me-2"), "ALCANCE POR LÍNEA DE ACCIÓN DE LA INSTANCIA"], 
                         style={'backgroundColor': '#1f2937', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div(dcc.Graph(figure=fig_variables, config={'displayModeBar': False}), className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4"), md=6),
            
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-graph-up me-2"), "COMPORTAMIENTO TEMPORAL: IMPACTO MENSUAL DE ATENCIONES"], 
                         style={'backgroundColor': '#1f2937', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div(dcc.Graph(figure=fig_temporal, config={'displayModeBar': False}), className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4"), md=6),
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
            ], className="shadow-sm mb-2"), md=12)
        ])
    ], style={'padding': '5px'})

    return layout_final
