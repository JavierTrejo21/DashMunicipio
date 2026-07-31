# areas/atencion_ciudadana.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

# Colores institucionales del municipio
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
TEXTO_DARK = "#1f2937"
GRIS_LIGHT = "#f8f9fa"
GRIS_BORDES = "#e5e7eb"

# Orden cronológico oficial para la secuencia de meses
ORDEN_MESES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

def analizar_atencion_ciudadana(df):
    """
    Módulo analítico premium para el área de 5.4 Atención Ciudadana.
    Presenta la distribución por áreas mediante un Treemap con paleta semafórica,
    tarjetas de indicadores estilo referencia y tabla/gráfica detallada.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Atención Ciudadana no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_atc = df.copy()
    df_atc.columns = [str(c).strip().upper() for c in df_atc.columns]
    columnas_reales = df_atc.columns.tolist()

    # Identificación flexible de columnas
    col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
    col_atn = next((c for c in columnas_reales if "ATEN" in c or "ATEND" in c), "ATENDIDOS")
    col_act = next((c for c in columnas_reales if "ACT" in c), "ACTIVIDAD")
    col_var = next((c for c in columnas_reales if "VAR" in c or "AREA" in c), "VARIABLE")
    col_con = next((c for c in columnas_reales if "CON" in c), "CONCEPTO")

    # --- LIMPIEZA RIGUROSA ---
    df_atc[col_atn] = pd.to_numeric(df_atc[col_atn], errors='coerce').fillna(0).astype(int)
    df_atc[col_var] = df_atc[col_var].fillna("OTRAS ÁREAS").astype(str).str.strip().str.upper()
    df_atc[col_act] = df_atc[col_act].fillna("SIN ESPECIFICAR").astype(str).str.strip()
    df_atc[col_mes] = df_atc[col_mes].fillna("S/M").astype(str).str.strip().str.upper()

    # --- CÁLCULO DE MÉTRICAS GENERALES PARA EL RESUMEN ---
    total_registros = len(df_atc)
    total_atendidos = int(df_atc[col_atn].sum())
    
    # Agrupación por área/variable para el Treemap y métricas
    df_areas = df_atc.groupby(col_var)[col_atn].sum().reset_index()
    df_areas = df_areas.sort_values(by=col_atn, ascending=False)
    
    area_mas_solicitada = df_areas.iloc[0][col_var] if not df_areas.empty else "N/D"
    max_atendidos_area = int(df_areas.iloc[0][col_atn]) if not df_areas.empty else 0

    # --- TARJETAS KPI ESTANDARIZADAS (CONTENEDOR Y TONO IDÉNTICOS A LA REFERENCIA) ---
    estilo_contenedor_ref = {
        "borderRadius": "10px", 
        "border": "1px solid #cbd5e1", 
        "backgroundColor": "#ffffff",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.02)"
    }

    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Small("TOTAL DE CIUDADANOS ATENDIDOS", className="d-block text-muted mb-1", style={"fontSize": "0.62rem", "letterSpacing": "1px", "fontWeight": "700"}),
                html.H3(f"{total_atendidos:,}", className="m-0", style={"color": "#1e293b", "fontSize": "1.25rem", "fontWeight": "700"})
            ], className="p-3 h-100 d-flex flex-column justify-content-center", style=estilo_contenedor_ref), 
            width=12, sm=6, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Small("ÁREA DE MAYOR AFLUENCIA", className="d-block text-muted mb-1", style={"fontSize": "0.62rem", "letterSpacing": "1px", "fontWeight": "700"}),
                html.H3(f"{area_mas_solicitada}", className="m-0 text-truncate", style={"color": "#1e293b", "fontSize": "1.1rem", "fontWeight": "700"})
            ], className="p-3 h-100 d-flex flex-column justify-content-center", style=estilo_contenedor_ref), 
            width=12, sm=6, className="mb-3"
        ),
    ], className="mb-2")

    # --- CONSTRUCCIÓN DEL TREEMAP SEMAFÓRICO ---
    fig_treemap = px.treemap(
        df_areas,
        path=[col_var],
        values=col_atn,
        color=col_atn,
        color_continuous_scale=[
            [0.0, '#93c5fd'],      # Azul claro (baja afluencia)
            [0.4, '#bc955c'],      # Dorado institucional (media afluencia)
            [1.0, '#691c32']       # Guinda institucional (alta concentración)
        ],
        custom_data=[col_atn]
    )

    fig_treemap.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,} ciudadanos",
        textposition="middle center",
        textfont=dict(size=15, family="Arial", color="white"),
        hovertemplate="<b>Área:</b> %{label}<br><b>Ciudadanos Atendidos:</b> %{value:,}<extra></extra>"
    )

    fig_treemap.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(
            title=dict(text="Afluencia", font=dict(size=11, family="Arial")),
            thickness=14,
            len=0.85
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420
    )

    # --- GRÁFICA DE LÍNEA TEMPORAL MENSUAL ---
    fig_linea = go.Figure()
    df_meses = df_atc.groupby(col_mes)[col_atn].sum().reset_index()
    df_meses['orden'] = df_meses[col_mes].apply(lambda x: ORDEN_MESES.index(x) if x in ORDEN_MESES else 99)
    df_meses = df_meses.sort_values('orden')

    if not df_meses.empty:
        fig_linea.add_trace(go.Scatter(
            x=df_meses[col_mes],
            y=df_meses[col_atn],
            mode='lines+markers+text',
            line=dict(color=GUINDA_INST, width=3, shape='spline'),
            marker=dict(color=DORADO_INST, size=9, line=dict(width=2, color="white")),
            text=df_meses[col_atn].apply(lambda x: f"<b>{int(x):,}</b>"),
            textposition="top center",
            textfont=dict(size=10, color=TEXTO_DARK, family="Arial"),
            fill='tozeroy',
            fillcolor='rgba(105, 28, 50, 0.04)',
            hovertemplate="<b>Mes:</b> %{x}<br><b>Atendidos:</b> %{y:,} ciudadanos<extra></extra>"
        ))

    fig_linea.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
        xaxis=dict(showgrid=False, tickfont=dict(color=TEXTO_DARK, size=10, family="Arial")),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", showticklabels=False)
    )

    # --- TABLA DE DETALLE ---
    columnas_tabla = [
        {"name": "Mes", "id": col_mes},
        {"name": "Área / Dirección", "id": col_var},
        {"name": "Actividad", "id": col_act},
        {"name": "Ciudadanos Atendidos", "id": col_atn}
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
        
        # Fila del Treemap Dimensional
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-grid-3x3-gap-fill me-2"), "CONCENTRACIÓN Y DISTRIBUCIÓN DE PRESENCIA CIUDADANA POR DEPARTAMENTO"], 
                         style={'backgroundColor': '#691c32', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Análisis volumétrico dimensional basado en registros de atención y audiencias ciudadanas.", 
                           className="text-center mb-2", 
                           style={"fontSize": "1rem", "color": "#1f2937", "fontWeight": "500"}),
                    dcc.Graph(figure=fig_treemap, config={'displayModeBar': False})
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=12)
        ]),

        # Fila de Gráfica Temporal
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-graph-up-arrow me-2"), "COMPORTAMIENTO HISTÓRICO Y FLUCTUACIÓN MENSUAL DE AUDIENCIAS"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Monitoreo temporal para identificar picos estacionales de solicitudes en el municipio.", 
                           className="text-center mb-1", 
                           style={"fontSize": "1rem", "color": "#1f2937", "fontWeight": "500"}),
                    dcc.Graph(figure=fig_linea, config={'displayModeBar': False})
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=12)
        ]),

        # Tabla Detallada
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    html.I(className="bi bi-table me-2", style={"color": "#bc955c"}),
                    "REGISTRO DETALLADO DE ATENCIÓN CIUDADANA"
                ], style={
                    'backgroundColor': '#691c32', 'color': 'white', 'padding': '12px 16px', 
                    'fontWeight': '700', 'fontSize': '0.8rem', 'borderRadius': '6px 6px 0 0'
                }),
                html.Div([
                    dash_table.DataTable(
                        data=df_atc.to_dict('records'),
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