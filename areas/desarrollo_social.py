# areas/desarrollo_social.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def analizar_desarrollo_social(df):
    """
    Módulo analítico premium para Dirección de Desarrollo Social.
    Sintaxis corregida y cálculos blindados contra pérdidas de columnas tras groupby.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Desarrollo Social no contiene registros válidos o está vacío.", color="warning")

    # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
    df_soc = df.copy()
    df_soc.columns = [str(c).strip().upper() for c in df_soc.columns]
    columnas_reales = df_soc.columns.tolist()

    # Identificación tolerante de columnas originales
    col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
    col_benef = next((c for c in columnas_reales if "BENEF" in c), "BENEFICIARIOS")
    col_act = next((c for c in columnas_reales if "ACT" in c), "ACTIVIDAD")
    col_var = next((c for c in columnas_reales if "VAR" in c), "VARIABLE")
    col_con = next((c for c in columnas_reales if "CON" in c), "CONCEPTO")
    col_com = next((c for c in columnas_reales if "COMUNIDAD" in c), "COMUNIDAD")

    # --- LIMPIEZA RIGUROSA Y VALORES POR DEFECTO ---
    df_soc[col_benef] = pd.to_numeric(df_soc[col_benef], errors='coerce').fillna(0).astype(int)
    df_soc[col_var] = df_soc[col_var].fillna("OTROS APOYOS").astype(str).str.strip().str.upper()
    df_soc[col_con] = df_soc[col_con].fillna("EN PROCESO / REGISTRADO").astype(str).str.strip().str.upper()
    df_soc[col_com] = df_soc[col_com].fillna("SIN ESPECIFICAR").astype(str).str.strip().str.upper()

    # --- CÁLCULO DE INDICADORES (KPIs) - MÉTODO SEGURO ---
    total_beneficiarios = int(df_soc[col_benef].sum())
    
    # Encontrar comunidad líder usando una columna temporal con nombre fijo ('TOTAL_APOYOS')
    df_top_com = df_soc.groupby(col_com)[col_benef].sum().reset_index(name='TOTAL_APOYOS')
    if not df_top_com.empty and df_top_com['TOTAL_APOYOS'].sum() > 0:
        idx_max = df_top_com['TOTAL_APOYOS'].idxmax()
        comunidad_lider = df_top_com.loc[idx_max, col_com]
        apoyos_lider = df_top_com.loc[idx_max, 'TOTAL_APOYOS']
        texto_comunidad = f"{comunidad_lider} ({int(apoyos_lider)} u.)"
    else:
        texto_comunidad = df_soc[col_com].value_counts().index[0] if not df_soc.empty else "Por definir"

    # Conteo de expedientes pendientes
    pendientes = int(df_soc[df_soc[col_con].str.contains("PENDIENTE", na=False)].shape[0])

    # --- DISEÑO DE TARJETAS INSTITUCIONALES (KPIs) ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#691c32", "borderRadius": "8px 0 0 8px"}),
                html.Small("CIUDADANOS BENEFICIADOS", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{total_beneficiarios:,.0f} Habs.", className="m-0 font-weight-bold mt-1", style={"color": "#691c32", "fontSize": "1.3rem"}),
                html.Small("Impacto social acumulado", className="text-muted d-block", style={"fontSize": "0.58rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#bc955c", "borderRadius": "8px 0 0 8px"}),
                html.Small("ZONA DE MAYOR ATENCIÓN TERRITORIAL", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(texto_comunidad, className="m-0 font-weight-bold mt-1", style={"color": "#1f2937", "fontSize": "1.1rem", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"}),
                html.Small("Localidad con más apoyos dispersados", className="text-muted d-block", style={"fontSize": "0.58rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#dc2626", "borderRadius": "8px 0 0 8px"}),
                html.Small("EXPEDIENTES PENDIENTES DE APROBACIÓN", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{pendientes} Casos", className="m-0 font-weight-bold mt-1", style={"color": "#dc2626", "fontSize": "1.3rem"}),
                html.Small("Requieren validación o desahogo", className="text-danger font-weight-bold d-block", style={"fontSize": "0.58rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=4, className="mb-3"
        ),
    ], className="mb-2")

    # --- GRÁFICA 1: DONA DE PROGRAMAS (CON COLUMNA FIJA) ---
    if total_beneficiarios > 0:
        df_prog = df_soc.groupby(col_var)[col_benef].sum().reset_index(name='VALOR_SUMADO')
    else:
        df_prog = df_soc.groupby(col_var).size().reset_index(name='VALOR_SUMADO')

    fig_programas = px.pie(
        df_prog, values='VALOR_SUMADO', names=col_var, hole=0.5,
        color_discrete_sequence=["#691c32", "#bc955c", "#1f2937"]
    )
    fig_programas.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=8.5)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )

    # --- GRÁFICA 2: SEMÁFORO DE GESTIÓN ---
    df_estatus = df_soc.groupby(col_con).size().reset_index(name='TOTAL')
    fig_estatus = px.bar(
        df_estatus, x='TOTAL', y=col_con, orientation='h',
        color=col_con,
        color_discrete_map={
            "ESTATUS PENDIENTE DE APROBACIÓN": "#dc2626",
            "ENTREGADO / CONCRETADO": "#10b981",
            "EN PROCESO / REGISTRADO": "#bc955c"
        }
    )
    fig_estatus.update_layout(
        margin=dict(l=10, r=10, t=15, b=15),
        xaxis=dict(title=None, gridcolor="#f3f4f6"), yaxis=dict(title=None),
        showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )

    # --- TABLA DE HISTORIAL DETALLADO ---
    columnas_tabla = [
        {"name": "Mes", "id": col_mes},
        {"name": "Localidad", "id": col_com},
        {"name": "Programa / Variable", "id": col_var},
        {"name": "Acción Operativa", "id": col_act},
        {"name": "Estatus de Gestión", "id": col_con},
        {"name": "Beneficiarios", "id": col_benef}
    ]

    # --- CONSTRUCCIÓN SEGURA DEL LAYOUT ---
    layout_final = html.Div([
        tarjetas_kpi,
        
        # Bloque de Gráficas Estilizadas
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-pie-chart-fill me-2"), "DISTRIBUCIÓN DEL IMPACTO POR POLÍTICA SOCIAL"], 
                         style={'backgroundColor': '#1f2937', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div(dcc.Graph(figure=fig_programas, config={'displayModeBar': False}), className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4"), md=6),
            
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-ui-checks me-2"), "SEMÁFORO DE CONTROL: ACCIONES EJECUTADAS VS. PENDIENTES"], 
                         style={'backgroundColor': '#1f2937', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div(dcc.Graph(figure=fig_estatus, config={'displayModeBar': False}), className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
            ], className="shadow-sm mb-4"), md=6),
        ]),

        # Bloque de la Tabla Histórica
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    html.I(className="bi bi-people-fill me-2", style={"color": "#bc955c"}),
                    "PADRÓN Y REGISTRO HISTÓRICO DE APOYOS DIRECTOS - DESARROLLO SOCIAL"
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
            ], className="shadow-sm mb-2"), md=12)
        ])
    ], style={'padding': '5px'})

    return layout_final
