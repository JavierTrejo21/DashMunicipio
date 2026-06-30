# areas/atencion_ciudadana.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

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
    Módulo analítico personalizado para el área de 5.4 Atención Ciudadana.
    Presenta la distribución por áreas mediante un Treemap semafórico e
    incorpora una gráfica de línea histórica mensual de alto impacto visual.
    """
    columnas_reales = df.columns.tolist()
    
    # Identificación flexible de columnas
    col_atendidos = next((c for c in columnas_reales if "ATEND" in str(c).upper()), None)
    col_area = next((c for c in columnas_reales if "VAR" in str(c).upper() or "AREA" in str(c).upper()), None)
    col_mes = next((c for c in columnas_reales if "MES" in str(c).upper()), None)

    # Validación de seguridad por si el archivo no corresponde
    if not all([col_atendidos, col_area]):
        return dbc.Alert(
            "⚠️ El archivo cargado no contiene las columnas requeridas ('ATENDIDOS' y 'VARIABLE').", 
            color="warning", 
            className="m-3"
        )

    # 1. LIMPIEZA Y PREPARACIÓN DE DATOS
    df_clean = df.copy()
    df_clean[col_atendidos] = pd.to_numeric(df_clean[col_atendidos], errors='coerce').fillna(0)
    df_clean[col_area] = df_clean[col_area].astype(str).str.strip().str.upper()
    
    if col_mes:
        df_clean[col_mes] = df_clean[col_mes].astype(str).str.strip().str.upper()

    # --- DATOS PARA EL TREEMAP ---
    df_areas = df_clean.groupby(col_area)[col_atendidos].sum().reset_index()
    df_areas = df_areas[df_areas[col_atendidos] > 0]

    if df_areas.empty:
        return dbc.Alert("📊 No hay registros válidos para procesar en este período.", color="info", className="m-3")

    # Cálculos ejecutivos para los KPIs
    total_atendidos = int(df_areas[col_atendidos].sum())
    df_ordenado = df_areas.sort_values(by=col_atendidos)
    area_mas_solicitada = df_ordenado.iloc[-1][col_area]
    max_atendidos_area = int(df_ordenado.iloc[-1][col_atendidos])

    # 2. CONSTRUCCIÓN DEL GRÁFICO 1: TREEMAP SEMAFÓRICO
    fig_treemap = px.treemap(
        df_areas,
        path=[col_area],
        values=col_atendidos,
        color=col_atendidos,
        color_continuous_scale=[
            [0.0, '#b2bec3'],      # Baja presencia: Gris acero
            [0.3, '#74b9ff'],      # Presencia moderada baja: Azul tenue
            [0.6, '#bc955c'],      # Concurrencia media: Dorado institucional
            [1.0, '#691c32']       # Alta concentración: Guinda institucional
        ],
        custom_data=[col_atendidos]
    )

    fig_treemap.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,} ciudadanos",
        textposition="middle center",
        textfont=dict(size=11, family="Arial", color="white"),
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
        height=400
    )

    # 3. CONSTRUCCIÓN DEL GRÁFICO 2: LÍNEA TEMPORAL DE ALTO IMPACTO (CORREGIDO)
    fig_linea = go.Figure()

    if col_mes:
        # Agrupamos por mes y sumamos ciudadanos
        df_meses = df_clean.groupby(col_mes)[col_atendidos].sum().reset_index()
        
        # Clasificar y ordenar bajo la secuencia lógica de meses del año
        df_meses['orden'] = df_meses[col_mes].apply(lambda x: ORDEN_MESES.index(x) if x in ORDEN_MESES else 99)
        df_meses = df_meses.sort_values('orden')
        
        # Crear la línea estilizada premium (Spline con área sombreada)
        fig_linea.add_trace(go.Scatter(
            x=df_meses[col_mes],
            y=df_meses[col_atendidos],
            mode='lines+markers+text',
            line=dict(color=GUINDA_INST, width=4, shape='spline'),                    # Curva suavizada guinda
            marker=dict(color=DORADO_INST, size=10, line=dict(width=2, color="white")), # CORRECCIÓN AQUÍ: Contorno blanco correcto
            text=df_meses[col_atendidos].apply(lambda x: f"<b>{int(x):,}</b>"),        # Datos visibles en negrita
            textposition="top center",
            textfont=dict(size=11, color=TEXTO_DARK, family="Arial"),
            fill='tozeroy',
            fillcolor='rgba(105, 28, 50, 0.04)',                                      # Sombra guinda muy sutil de fondo
            hovertemplate="<b>Mes:</b> %{x}<br><b>Atendidos:</b> %{y:,} ciudadanos<extra></extra>"
        ))
    else:
        fig_linea.add_trace(go.Scatter(text="Información histórica no disponible en este archivo."))

    fig_linea.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=280, # Altura calculada para ser alargada horizontalmente
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=TEXTO_DARK, size=11, family="Arial")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f3f4f6",
            showticklabels=False, # Ocultamos el eje Y para no saturar
            range=[0, df_meses[col_atendidos].max() * 1.25] if col_mes and not df_meses.empty else None
        )
    )

    # 4. INTERFAZ VISUAL DEL MÓDULO (LAYOUT CONSOLIDADO)
    return html.Div([
        # Fila de Indicadores Rápidos (KPIs)
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("TOTAL DE CIUDADANOS ATENDIDOS", className="text-muted small font-weight-bold mb-2", style={"letterSpacing": "0.5px"}),
                        html.H3(f"{total_atendidos:,}", style={"color": GUINDA_INST, "fontWeight": "bold", "margin": "0"})
                    ], className="d-flex flex-column justify-content-center h-100")
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "10px", "borderLeft": f"5px solid {GUINDA_INST}"}),
                width=12, md=6, className="mb-3 mb-md-0"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("ÁREA DE MAYOR CONCENTRACIÓN CIUDADANA", className="text-muted small font-weight-bold mb-2", style={"letterSpacing": "0.5px"}),
                        html.H5(f"{area_mas_solicitada}", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.15rem", "margin": "0", "lineHeight": "1.2"}),
                        html.Small(f"Registra {max_atendidos_area:,} ciudadanos atendidos.", className="text-secondary mt-1 d-block")
                    ], className="d-flex flex-column justify-content-center h-100")
                ], className="border-0 shadow-sm h-100", style={"borderRadius": "10px", "borderLeft": f"5px solid {DORADO_INST}"}),
                width=12, md=6
            )
        ], className="g-3 px-3 pt-3 align-items-stretch"),

        # Fila del Treemap Dimensional
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Div([
                        html.H5("Concentración y Distribución de Presencia Ciudadana por Departamento", 
                                style={"color": GUINDA_INST, "fontWeight": "600", "margin": "0", "fontFamily": "Arial"}),
                        html.P("Análisis volumétrico dimensional basado en registros de atención y audiencias ciudadanas.", 
                               className="text-muted small mb-0", style={"marginTop": "2px"})
                    ], style={"borderBottom": f"1px solid {GRIS_BORDES}", "paddingBottom": "12px", "marginBottom": "15px"}),
                    
                    dcc.Graph(figure=fig_treemap, config={"displayModeBar": False})
                ], className="bg-white p-4 border shadow-sm", style={"borderRadius": "14px", "marginTop": "20px"}),
                width=12
            )
        ], className="g-3 px-3"),

        # Fila de la Gráfica de Línea Temporal (Abajo y Alargada)
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Div([
                        html.H5("Comportamiento Histórico y Fluctuación Mensual de Audiencias", 
                                style={"color": GUINDA_INST, "fontWeight": "600", "margin": "0", "fontFamily": "Arial"}),
                        html.P("Monitoreo temporal para identificar picos estacionales de solicitudes en el municipio.", 
                               className="text-muted small mb-0", style={"marginTop": "2px"})
                    ], style={"borderBottom": f"1px solid {GRIS_BORDES}", "paddingBottom": "12px", "marginBottom": "10px"}),
                    
                    dcc.Graph(figure=fig_linea, config={"displayModeBar": False})
                ], className="bg-white p-4 border shadow-sm", style={"borderRadius": "14px", "marginTop": "20px"}),
                width=12
            )
        ], className="g-3 px-3 pb-3")
    ])
