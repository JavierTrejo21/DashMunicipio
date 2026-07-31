# areas/mujeres.py
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def analizar_instancia_mujeres(df):
    """
    Módulo analítico premium para la Instancia Municipal de las Mujeres.
    Muestra los indicadores con tarjetas idénticas en estilo, tono y contenedor a la referencia.
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

    # --- CÁLCULO DE MÉTRICAS GENERALES PARA EL RESUMEN DEL ÁREA ---
    total_registros = len(df_muj)
    total_atendidos = int(df_muj[col_atn].sum())
    
    df_canalizaciones = df_muj[df_muj[col_var].str.contains("CANALIZA", na=False)]
    total_canalizados = int(df_canalizaciones[col_atn].sum()) if not df_canalizaciones.empty else 0

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
                html.Small("TOTAL DE ACTIVIDADES", className="d-block text-muted mb-1", style={"fontSize": "0.62rem", "letterSpacing": "1px", "fontWeight": "700"}),
                html.H3(f"{total_registros:,}", className="m-0", style={"color": "#1e293b", "fontSize": "1.25rem", "fontWeight": "700"})
            ], className="p-3 h-100 d-flex flex-column justify-content-center", style=estilo_contenedor_ref), 
            width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Small("PERSONAS ATENDIDAS", className="d-block text-muted mb-1", style={"fontSize": "0.62rem", "letterSpacing": "1px", "fontWeight": "700"}),
                html.H3(f"{total_atendidos:,}", className="m-0", style={"color": "#1e293b", "fontSize": "1.25rem", "fontWeight": "700"})
            ], className="p-3 h-100 d-flex flex-column justify-content-center", style=estilo_contenedor_ref), 
            width=12, sm=4, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Small("CASOS CANALIZADOS", className="d-block text-muted mb-1", style={"fontSize": "0.62rem", "letterSpacing": "1px", "fontWeight": "700"}),
                html.H3(f"{total_canalizados:,}", className="m-0", style={"color": "#1e293b", "fontSize": "1.25rem", "fontWeight": "700"})
            ], className="p-3 h-100 d-flex flex-column justify-content-center", style=estilo_contenedor_ref), 
            width=12, sm=4, className="mb-3"
        ),
    ], className="mb-2")

    # --- PANEL DE PROGRESO CON PALETA INSTITUCIONAL ---
    df_var_filtrado = df_muj[~df_muj[col_var].str.contains("MUJERES BENEFICIARIAS", na=False)]
    
    df_var_agrupado = df_var_filtrado.groupby(col_var).agg(
        TOTAL_VALOR=(col_atn, 'sum'),
        CANTIDAD_REGISTROS=(col_act, 'count')
    ).reset_index()
    
    df_var_agrupado = df_var_agrupado.sort_values(by='TOTAL_VALOR', ascending=False)
    max_val = df_var_agrupado['TOTAL_VALOR'].max() if not df_var_agrupado.empty else 1
    
    colores_institucionales = ["#691c32", "#115e59", "#bc955c", "#374151", "#047857", "#1e40af"]

    items_lineas_accion = []
    for i, row in df_var_agrupado.iterrows():
        nombre_var = str(row[col_var])
        val = row['TOTAL_VALOR']
        num_regs = row['CANTIDAD_REGISTROS']
        porcentaje = min(int((val / max_val) * 100), 100) if max_val > 0 else 0
        color = colores_institucionales[i % len(colores_institucionales)]
        
        if "TALLER" in nombre_var:
            texto_num = f"{num_regs}"
            texto_unidad = "talleres" if num_regs != 1 else "taller"
        elif "INSTITUC" in nombre_var:
            texto_num = f"{val}"
            texto_unidad = "inst." if val != 1 else "inst."
        elif "RED" in nombre_var:
            texto_num = f"{val}"
            texto_unidad = "redes" if val != 1 else "red"
        elif "CANALIZA" in nombre_var:
            texto_num = f"{val}"
            texto_unidad = "casos" if val != 1 else "caso"
        else:
            texto_num = f"{val}"
            texto_unidad = "acciones"

        item = html.Div([
            html.Div([
                html.Span(nombre_var.title(), className="d-block mb-1", style={"fontSize": "0.75rem", "fontWeight": "700", "color": "#111827"}),
                html.Div(
                    html.Div(style={"width": f"{porcentaje}%", "backgroundColor": color, "height": "8px", "borderRadius": "4px"}),
                    className="w-100", style={"height": "8px", "borderRadius": "4px", "backgroundColor": "#e5e7eb"}
                )
            ], style={"flex": "1", "paddingRight": "20px"}),
            
            html.Div([
                html.Span(texto_num, style={"fontSize": "0.9rem", "fontWeight": "800", "color": color}),
                html.Span(f" {texto_unidad}", style={"fontSize": "0.7rem", "fontWeight": "600", "color": "#4b5563", "marginLeft": "3px"})
            ], style={"minWidth": "90px", "textAlign": "right", "display": "flex", "align-items": "baseline", "justify-content": "flex-end"})
            
        ], className="mb-3 pb-2 border-bottom d-flex align-items-center justify-content-between")
        
        items_lineas_accion.append(item)

    panel_progreso_limpio = html.Div(
        items_lineas_accion if items_lineas_accion else [html.P("Sin registros disponibles.", className="text-muted text-center")],
        style={"maxHeight": "240px", "overflowY": "auto", "paddingRight": "5px"}
    )

    # --- GRÁFICA 2: COMPORTAMIENTO TEMPORAL ---
    df_mes_agrupado = df_muj.groupby(col_mes)[col_atn].sum().reset_index(name='TOTAL_MES')
    meses_orden = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    df_mes_agrupado[col_mes] = pd.Categorical(df_mes_agrupado[col_mes], categories=meses_orden, ordered=True)
    df_mes_agrupado = df_mes_agrupado.sort_values(col_mes).dropna()

    fig_temporal = go.Figure()
    
    for i, row in df_mes_agrupado.iterrows():
        mes = row[col_mes]
        val = row['TOTAL_MES']
        color_b = colores_institucionales[i % len(colores_institucionales)]
        
        fig_temporal.add_trace(go.Bar(
            x=[mes], y=[val],
            marker_color=color_b,
            showlegend=False,
            hoverinfo='x+y'
        ))

    anotaciones_pines = []
    for i, row in df_mes_agrupado.iterrows():
        mes = row[col_mes]
        val = row['TOTAL_MES']
        color_b = colores_institucionales[i % len(colores_institucionales)]
        
        anotaciones_pines.append(dict(
            x=mes, y=val,
            text=f"<b>{val}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor=color_b,
            ax=0,
            ay=-30,
            bgcolor="white",
            bordercolor=color_b,
            borderwidth=2,
            borderpad=3,
            font=dict(size=10, color=color_b)
        ))

    fig_temporal.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title=None, tickfont=dict(size=10, color="#1f2937"), gridcolor="#f3f4f6"),
        yaxis=dict(title=None, tickfont=dict(size=10, color="#1f2937"), gridcolor="#f3f4f6"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
        annotations=anotaciones_pines
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
        
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-list-check me-2"), "INDICADORES DE PROGRESO POR LÍNEA DE ACCIÓN"], 
                         style={'backgroundColor': '#115e59', 'color': 'white', 'padding': '10px 14px', 'fontWeight': 'bold', 'fontSize': '0.72rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div([
                    html.P("Desglose operativo y volumétrico por programa secundario.", 
                           className="text-center mb-3", 
                           style={"fontSize": "0.68rem", "color": "#1f2937", "fontWeight": "500"}),
                    panel_progreso_limpio
                ], className="p-3 border border-top-0 bg-white", style={"borderRadius": "0 0 6px 6px", "minHeight": "280px"})
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