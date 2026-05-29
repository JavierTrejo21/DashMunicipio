import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

def cargar_datos_atencion():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM atencion_ciudadana", conn)
    conn.close()
    return df

def layout_atencion():
    return html.Div([
        html.H2("🤝 5.1.2 ATENCIÓN CIUDADANA - PANEL ESTRATÉGICO", style={'color': '#691c32', 'fontWeight': 'bold'}),
        html.Hr(),

        # --- FILTROS ---
        dbc.Row([
            dbc.Col([
                html.Label("Seleccionar Mes:", className="fw-bold"),
                dcc.Dropdown(
                    id='at-mes', 
                    options=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'], 
                    multi=True, 
                    placeholder="Todos los meses"
                )
            ], md=12),
        ], className="mb-4 p-3 bg-white shadow-sm rounded"),

        # --- TARJETAS DINÁMICAS ---
        dbc.Row([
            dbc.Col(id='at-card-ciudadanos', md=4),
            dbc.Col(id='at-card-eficiencia', md=4),
            dbc.Col(id='at-card-alcance', md=4),
        ], className="mb-4"),

        # --- GRÁFICAS DE ALTO IMPACTO ---
        dbc.Row([
            # Gráfica 1: Canalización por Área (TreeMap)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("FLUJO DE CANALIZACIÓN POR ÁREA", className="fw-bold bg-dark text-white"),
                    dbc.CardBody([
                        dcc.Graph(id='graph-at-canalizacion', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], md=7),
            
            # Gráfica 2: Atenciones por Localidad (Ranking)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("RANKING DE ATENCIÓN POR LOCALIDAD", className="fw-bold"),
                    dbc.CardBody([
                        dcc.Graph(id='graph-at-localidades', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], md=5),
        ], className="mb-4"),

        # --- TABLA DE RESUMEN EJECUTIVO ---
        dbc.Card([
            dbc.CardHeader("REGISTRO DETALLADO DE ATENCIONES", className="bg-light text-dark fw-bold"),
            dbc.CardBody([
                html.Div(id='at-tabla-full')
            ])
        ], className="shadow-sm mb-5")
    ], className="p-3")

@callback(
    [Output('at-card-ciudadanos', 'children'),
     Output('at-card-eficiencia', 'children'),
     Output('at-card-alcance', 'children'),
     Output('graph-at-canalizacion', 'figure'),
     Output('graph-at-localidades', 'figure'),
     Output('at-tabla-full', 'children')],
    [Input('at-mes', 'value')]
)
def actualizar_atencion(meses):
    df = cargar_datos_atencion()
    if meses:
        df = df[df['mes'].isin(meses)]

    # --- MÉTRICAS ---
    total_atendidos = df['cantidad'].sum()
    total_localidades = df[df['actividad_tipo'] == 'ATENCION_LOCALIDAD']['area_o_localidad'].nunique()
    
    df_areas = df[df['actividad_tipo'] == 'CANALIZACION']
    area_mas_solicitada = df_areas.groupby('area_o_localidad')['cantidad'].sum().idxmax() if not df_areas.empty else "N/A"

    # --- GRÁFICA 1: TREEMAP (Muy visual para ver áreas grandes) ---
    fig_tree = px.treemap(df_areas, path=['area_o_localidad'], values='cantidad',
                          color='cantidad', color_continuous_scale='Viridis',
                          title="Volumen de Trámites por Departamento")
    fig_tree.update_layout(margin=dict(l=0, r=0, t=30, b=0))

    # --- GRÁFICA 2: RANKING HORIZONTAL ---
    df_loc = df[df['actividad_tipo'] == 'ATENCION_LOCALIDAD'].groupby('area_o_localidad')['cantidad'].sum().nlargest(10).reset_index()
    fig_rank = px.bar(df_loc, x='cantidad', y='area_o_localidad', orientation='h',
                      color='cantidad', color_continuous_scale='Bluered')
    fig_rank.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0), yaxis_title=None)

    # --- COMPONENTES VISUALES ---
    def crear_tarjeta(titulo, valor, color, icono):
        return dbc.Card([
            dbc.CardBody([
                html.H6([html.I(className=f"bi bi-{icono} me-2"), titulo], className="text-muted"),
                html.H2(valor, style={'color': color, 'fontWeight': 'bold'})
            ])
        ], className="text-center shadow-sm border-0", style={'borderTop': f'5px solid {color}'})

    c1 = crear_card_atencion("Ciudadanos Atendidos", f"{int(total_atendidos):,}", "#691c32", "people-fill")
    c2 = crear_card_atencion("Área con más Carga", area_mas_solicitada, "#bc955c", "diagram-3-fill")
    c3 = crear_card_atencion("Cobertura Local", f"{total_localidades} Com.", "#2d2d2d", "geo-alt-fill")

    # Tabla
    tabla = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i.upper(), "id": i} for i in df.columns if i not in ['id', 'anio', 'trimestre']],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '10px'}
    )

    return c1, c2, c3, fig_tree, fig_rank, tabla

def crear_card_atencion(titulo, valor, color, icono):
    return dbc.Card([
        dbc.CardBody([
            html.H6([html.I(className=f"bi bi-{icono} me-2"), titulo], className="text-muted"),
            html.H2(valor, style={'color': color, 'fontWeight': 'bold'})
        ])
    ], className="text-center shadow-sm border-0", style={'borderTop': f'5px solid {color}'})
