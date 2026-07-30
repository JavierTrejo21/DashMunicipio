# areas/desarrollo_social.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def analizar_desarrollo_social(df):
    """
    Módulo analítico premium para Dirección de Desarrollo Social.
    Actualizado con subtítulos de alta legibilidad y estilo infográfico moderno.
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

    # --- TARJETAS SUPERIORES ESTILO INFOGRÁFICO ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#691c32", "borderRadius": "8px 0 0 8px"}),
                html.Small("CIUDADANOS BENEFICIADOS", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"{total_beneficiarios:,.0f} Habs.", className="m-0 font-weight-bold mt-1", style={"color": "#691c32", "fontSize": "1.2rem"}),
                html.Small("Impacto social acumulado", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#115e59", "borderRadius": "8px 0 0 8px"}),
                html.Small("ZONA DE MAYOR ATENCIÓN TERRITORIAL", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.Div(texto_comunidad, className="m-0 font-weight-bold mt-1", style={"color": "#115e59", "fontSize": "0.95rem", "lineHeight": "1.2", "wordBreak": "break-word"}),
                html.Small("Localidad con más apoyos dispersados", className="font-weight-bold d-block mt-1", style={"fontSize": "0.6rem", "color": "#374151"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#dc2626", "borderRadius": "8px 0 0 8px"}),
                html.Small("EXPEDIENTES PENDIENTES DE APROBACIÓN", className="font-weight-bold d-block", style={"fontSize": "0.7rem", "letterSpacing": "0.5px", "color": "#1f2937"}),
                html.H3(f"{pendientes} Casos", className="m-0 font-weight-bold mt-1", style={"color": "#dc2626", "fontSize": "1.2rem"}),
                html.Small("Requieren validación o desahogo", className="font-weight-bold d-block", style={"fontSize": "0.6rem", "color": "#991b1b"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
    ], className="mb-2")

    # --- GRÁFICA 1: ANILLO INFOGRÁFICO DE DISTRIBUCIÓN ---
    df_prog = df_soc.groupby(col_act).size().reset_index(name='CONTEO')
    df_prog = df_prog.sort_values(by='CONTEO', ascending=False).reset_index(drop=True)

    fig_programas = go.Figure(data=[go.Pie(
        labels=df_prog[col_act],
        values=df_prog['CONTEO'],
        hole=0.6,
        textinfo='percent',
        textposition='inside',
        insidetextfont=dict(color='white', size=11, family="sans-serif", weight="bold"),
        marker=dict(colors=["#115e59", "#691c32", "#bc955c", "#4b5563", "#9ca3af"]),
        hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )])

    fig_programas.update_layout(
        annotations=[dict(text=f"<b>{total_expedientes}</b><br>Total", x=0.5, y=0.5, font_size=13, font_color="#1f2937", showarrow=False)],
        margin=dict(l=10, r=130, t=10, b=10),
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

    # --- GRÁFICA 2: INDICADOR TIPO GAUGE / RADIAL DE CUMPLIMIENTO ---
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=porcentaje_eficacia,
        number=dict(suffix="%", font=dict(color="#115e59", size=26, family="sans-serif")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor="#1f2937"),
            bar=dict(color="#115e59"),
            bgcolor="white",
            borderwidth=2,
            bordercolor="#e5e7eb",
            steps=[
                dict(range=[0, 50], color="#f3f4f6"),
                dict(range=[50, 80], color="#e5e7eb"),
                dict(range=[80, 100], color="#d1d5db")
            ],
            threshold=dict(
                line=dict(color="#691c32", width=4),
                thickness=0.75,
                value=porcentaje_eficacia
            )
        )
    ))

    fig_gauge.update_layout(
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=240
    )

    # --- TABLA DE HISTORIAL DETALLADO ---
    columnas_tabla = [
        {"name": "Mes", "id": col_mes},
        {"name": "Localidad", "id": col_com},
        {"name": "Estatus (Variable)", "id": col_var},
        {"name": "Acción Operativa / Actividad", "id": col_act},
        {"name": "Beneficiarios", "id": col_benef}
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

    # --- CONSTRUCCIÓN DEL LAYOUT FINAL ---
    layout_final = html.Div([
        estilos_animacion,
        tarjetas_kpi,
        
        # Bloque de Visualizaciones con Estilo Infográfico
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-pie-chart-fill me-2"), "DISTRIBUCIÓN POR PROGRAMA SOCIAL (ANILLO INFOGRÁFICO)"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div(dcc.Graph(figure=fig_programas, config={'displayModeBar': False}), className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=6),
            
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-speedometer2 me-2"), "EFICACIA GLOBAL DE GESTIÓN (INDICADOR RADIAL)"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    # Texto con color oscuro de alta legibilidad y grosor medio
                    html.P("Porcentaje consolidado de expedientes concluidos vs. meta institucional.", 
                           className="text-center mb-1", 
                           style={"fontSize": "0.68rem", "color": "#1f2937", "fontWeight": "500"}),
                    dcc.Graph(figure=fig_gauge, config={'displayModeBar': False})
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4 animar-entrada"), md=6),
        ]),

        # Bloque de la Tabla Histórica
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    html.I(className="bi bi-people-fill me-2", style={"color": "#bc955c"}),
                    "PADRÓN GENERAL Y HISTÓRICO DE APOYOS DIRECTOS - DESARROLLO SOCIAL"
                ], style={
                    'backgroundColor': '#691c32', 'color': 'white', 'padding': '12px 16px', 
                    'fontWeight': '700', 'fontSize': '0.8rem', 'borderRadius': '6px 6px 0 0'
                }),
                html.Div([
                    dash_table.DataTable(
                        data=df_soc.to_dict('records'),
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

    return layout_final