# areas/pueblos_indigenas.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def analizar_pueblos_indigenas(df):
    """
    Módulo analítico premium e independiente para la Dirección de Pueblos Indígenas.
    Actualizado con estilo infográfico institucional y máxima legibilidad.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Pueblos Indígenas no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_ind = df.copy()
    df_ind.columns = [str(c).strip().upper() for c in df_ind.columns]
    columnas_reales = df_ind.columns.tolist()

    # Mapeo tolerante de nombres de columnas basados en el archivo real
    col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
    col_comunidad = next((c for c in columnas_reales if "COMUNIDAD" in c or "LOC" in c), "COMUNIDAD")
    col_lengua = next((c for c in columnas_reales if "LENGUA" in c or "MATERNA" in c), None)
    col_benef = next((c for c in columnas_reales if "BENEF" in c or "ATEND" in c), "BENEFICIARIOS")
    col_prog = next((c for c in columnas_reales if "PROG" in c or "TIPO" in c), "TIPO DE PROGRAMA")
    col_inv = next((c for c in columnas_reales if "INV" in c), "INVERSION")

    # --- LIMPIEZA RIGUROSA DE DATOS ---
    if col_benef in df_ind.columns:
        df_ind[col_benef] = pd.to_numeric(df_ind[col_benef], errors='coerce').fillna(0)
    else:
        df_ind['BENEFICIARIOS_LIMPIO'] = 1
        col_benef = 'BENEFICIARIOS_LIMPIO'

    if col_inv in df_ind.columns:
        df_ind[col_inv] = df_ind[col_inv].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
        df_ind[col_inv] = pd.to_numeric(df_ind[col_inv], errors='coerce').fillna(0)
    else:
        df_ind['INVERSION_LIMPIA'] = 0
        col_inv = 'INVERSION_LIMPIA'

    # --- CÁLCULO DE MÉTRICAS EJECUTIVAS (KPIs) ---
    total_inversion = df_ind[col_inv].sum()
    total_beneficiarios = df_ind[col_benef].sum()
    total_expedientes = len(df_ind)
    
    if col_lengua:
        comunidades_lengua = df_ind[df_ind[col_lengua].astype(str).str.upper().str.strip() == "SI"][col_comunidad].nunique()
    else:
        comunidades_lengua = df_ind[col_comunidad].nunique()

    # --- DISEÑO DE TARJETAS INSTITUCIONALES (KPIs) ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#691c32", "borderRadius": "8px 0 0 8px"}),
                html.Small("INVERSIÓN TOTAL ASIGNADA", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"${total_inversion:,.2f}", className="m-0 font-weight-bold mt-1", style={"color": "#691c32", "fontSize": "1.2rem"}),
                html.Small("Fondos ejecutados y apoyos económicos", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#115e59", "borderRadius": "8px 0 0 8px"}),
                html.Small("POBLACIÓN INDÍGENA BENEFICIADA", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"{total_beneficiarios:,.0f} Habs.", className="m-0 font-weight-bold mt-1", style={"color": "#115e59", "fontSize": "1.2rem"}),
                html.Small("Ciudadanos atendidos de manera directa", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#bc955c", "borderRadius": "8px 0 0 8px"}),
                html.Small("LOCALIDADES CON LENGUA MATERNA", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"{comunidades_lengua} Comunidades", className="m-0 font-weight-bold mt-1", style={"color": "#bc955c", "fontSize": "1.2rem"}),
                html.Small("Identidad cultural y hablantes activos", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
    ], className="mb-2")

    # --- GRÁFICA 1: ANILLO INFOGRÁFICO DE PROGRAMAS INDÍGENAS ---
    df_ind[col_prog] = df_ind[col_prog].fillna("POR CLASIFICAR").astype(str).str.strip()
    df_programas = df_ind.groupby(col_prog).size().reset_index(name='CONTEO')
    df_programas = df_programas.sort_values(by='CONTEO', ascending=False).reset_index(drop=True)

    fig_programas = go.Figure(data=[go.Pie(
        labels=df_programas[col_prog],
        values=df_programas['CONTEO'],
        hole=0.6,
        textinfo='percent',
        textposition='inside',
        insidetextfont=dict(color='white', size=11, family="sans-serif", weight="bold"),
        marker=dict(colors=["#691c32", "#115e59", "#bc955c", "#4b5563", "#2563eb", "#d97706", "#8b5cf6"]),
        hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )])

    fig_programas.update_layout(
        annotations=[dict(text=f"<b>{total_expedientes}</b><br>Total", x=0.5, y=0.5, font_size=13, font_color="#1f2937", showarrow=False)],
        margin=dict(l=10, r=140, t=10, b=10),
        legend=dict(
            orientation="v", 
            yanchor="middle", 
            y=0.5, 
            xanchor="left", 
            x=1.02, 
            font=dict(size=9, color="#1f2937")
        ),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        height=280
    )

    # --- GRÁFICA 2: IMPACTO POR LOCALIDAD (BARRAS HORIZONTALES ESTILIZADAS) ---
    df_comunidades = df_ind.groupby(col_comunidad)[col_benef].sum().reset_index(name='TOTAL_BENEF').sort_values(by='TOTAL_BENEF', ascending=True).tail(8)
    
    fig_comunidades = px.bar(
        df_comunidades,
        x='TOTAL_BENEF',
        y=col_comunidad,
        orientation='h',
        color_discrete_sequence=["#115e59"],
        labels={'TOTAL_BENEF': 'Ciudadanos', col_comunidad: 'Comunidad'}
    )
    fig_comunidades.update_layout(
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis=dict(title=None, gridcolor="#f3f4f6", tickfont=dict(size=10, color="#1f2937")),
        yaxis=dict(title=None, tickfont=dict(size=10, color="#1f2937")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=280
    )

    # --- TABLA DE REGISTROS HISTÓRICOS ---
    df_ind["INVERSION_M"] = df_ind[col_inv].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")
    
    columnas_tabla = [
        {"name": "Periodo / Mes", "id": col_mes},
        {"name": "Comunidad Indígena", "id": col_comunidad},
        {"name": "Programa o Apoyo Otorgado", "id": col_prog},
        {"name": "Hablantes Maternos", "id": col_lengua if col_lengua else col_comunidad},
        {"name": "Población Atendida", "id": col_benef},
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
        
        # Bloque de Visualizaciones Infográficas
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-pie-chart-fill me-2"), "PARTICIPACIÓN DE PROGRAMAS SOCIALES EN COMUNIDADES"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Distribución porcentual de apoyos otorgados por tipo de programa.", 
                           className="text-center mb-1", 
                           style={"fontSize": "0.68rem", "color": "#1f2937", "fontWeight": "500"}),
                    dcc.Graph(figure=fig_programas, config={'displayModeBar': False})
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=6),
            
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-bar-chart-line-fill me-2"), "TOP LOCALIDADES INDÍGENAS CON MAYOR IMPACTO DE ATENCIÓN"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Localidades con mayor volumen de población indígena beneficiada.", 
                           className="text-center mb-1", 
                           style={"fontSize": "0.68rem", "color": "#1f2937", "fontWeight": "500"}),
                    dcc.Graph(figure=fig_comunidades, config={'displayModeBar': False})
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=6),
        ]),

        # Bloque de la Tabla del Padrón
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    html.I(className="bi bi-journal-text me-2", style={"color": "#bc955c"}),
                    "PADRÓN COMPLETO Y HISTÓRICO DE ATENCIÓN A COMUNIDADES INDÍGENAS"
                ], style={
                    'backgroundColor': '#691c32', 'color': 'white', 'padding': '12px 16px', 
                    'fontWeight': '700', 'fontSize': '0.8rem', 'borderRadius': '6px 6px 0 0'
                }),
                html.Div([
                    dash_table.DataTable(
                        data=df_ind.to_dict('records'),
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