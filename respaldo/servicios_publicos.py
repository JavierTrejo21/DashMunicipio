import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

def cargar_datos():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM servicios_publicos", conn)
    conn.close()
    
    # 1. Limpieza de Inversión
    df['inversion_num'] = pd.to_numeric(df['materiales_utilizados'], errors='coerce').fillna(0)
    
    # 2. Extracción de Beneficiarios
    df['beneficiarios_num'] = df['observaciones'].str.extract(r'Beneficiarios: (\d+)').astype(float).fillna(0)
    
    # 3. Lógica de Trimestres
    # Mapeamos los meses a sus respectivos periodos
    mapa_trimestres = {
        'ENERO': '1er Trimestre', 'FEBRERO': '1er Trimestre', 'MARZO': '1er Trimestre',
        'ABRIL': '2do Trimestre', 'MAYO': '2do Trimestre', 'JUNIO': '2do Trimestre',
        'JULIO': '3er Trimestre', 'AGOSTO': '3er Trimestre', 'SEPTIEMBRE': '3er Trimestre',
        'OCTUBRE': '4to Trimestre', 'NOVIEMBRE': '4to Trimestre', 'DICIEMBRE': '4to Trimestre'
    }
    df['trimestre'] = df['fecha_de_reporte'].str.upper().map(mapa_trimestres).fillna('Sin Clasificar')
    
    # 4. Año (Si no viene en el CSV, asumimos 2026 o el año actual)
    # Si tu CSV tuviera columna 'ANIO', usaríamos esa. Por ahora creamos una fija para el filtro.
    df['anio'] = "2026" 
    
    return df

def layout_servicios():
    df = cargar_datos()
    
    return html.Div([
        html.H2("📊 CONTROL DE AVANCES: SERVICIOS PÚBLICOS", 
                style={'color': '#691c32', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Hr(style={'borderTop': '3px solid #bc955c'}),

        # --- SECCIÓN DE SEGMENTADORES TEMPORALES (ARRIBA) ---
        dbc.Card([
            dbc.CardHeader("FILTROS DE TEMPORALIDAD Y AVANCE", className="bg-dark text-white fw-bold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("📅 Año:", className="fw-bold"),
                        dcc.Dropdown(id='f-anio', options=['2025', '2026'], value='2026', clearable=False)
                    ], md=4),
                    dbc.Col([
                        html.Label("⏱️ Trimestre:", className="fw-bold"),
                        dcc.Dropdown(
                            id='f-trimestre', 
                            options=[{'label': t, 'value': t} for t in ['1er Trimestre', '2do Trimestre', '3er Trimestre', '4to Trimestre']],
                            multi=True, placeholder="Filtrar por periodo..."
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("📆 Mes:", className="fw-bold"),
                        dcc.Dropdown(
                            id='f-mes', 
                            options=[{'label': m, 'value': m} for m in df['fecha_de_reporte'].unique()],
                            multi=True, placeholder="Meses específicos..."
                        )
                    ], md=4),
                ])
            ])
        ], className="mb-4 shadow-sm"),

        # --- SEGMENTADORES OPERATIVOS (ABAJO) ---
        dbc.Row([
            dbc.Col([
                html.Label("📍 Localidad:", className="fw-bold"),
                dcc.Dropdown(id='f-comuna', options=[{'label': c, 'value': c} for c in sorted(df['ubicacion_o_localidad'].unique())], multi=True)
            ], md=6),
            dbc.Col([
                html.Label("🛠️ Actividad:", className="fw-bold"),
                dcc.Dropdown(id='f-serv', options=[{'label': s, 'value': s} for s in sorted(df['tipo_de_servicio'].unique())], multi=True)
            ], md=6),
        ], className="mb-4"),

        # --- INDICADORES ---
        dbc.Row([
            dbc.Col(id='kpi-inv', md=4),
            dbc.Col(id='kpi-ben', md=4),
            dbc.Col(id='kpi-reg', md=4),
        ], className="mb-4"),

        # --- GRÁFICAS ---
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-pie'), md=6),
            dbc.Col(dcc.Graph(id='graph-bar'), md=6),
        ]),

        # --- TABLA ---
        html.Div(id='table-container', className="mt-4")
    ], className="p-4")

# === CALLBACK UNIFICADO ===
@callback(
    [Output('kpi-inv', 'children'), Output('kpi-ben', 'children'), Output('kpi-reg', 'children'),
     Output('graph-pie', 'figure'), Output('graph-bar', 'figure'), Output('table-container', 'children')],
    [Input('f-anio', 'value'), Input('f-trimestre', 'value'), Input('f-mes', 'value'),
     Input('f-comuna', 'value'), Input('f-serv', 'value')]
)
def filtrar_todo(anio, trim, mes, comuna, serv):
    df = cargar_datos()

    # Aplicación de filtros en cascada
    if anio: df = df[df['anio'] == anio]
    if trim: df = df[df['trimestre'].isin(trim)]
    if mes:  df = df[df['fecha_de_reporte'].isin(mes)]
    if comuna: df = df[df['ubicacion_o_localidad'].isin(comuna)]
    if serv: df = df[df['tipo_de_servicio'].isin(serv)]

    # KPIs
    inv = df['inversion_num'].sum()
    ben = int(df['beneficiarios_num'].sum())
    
    # Creación de visuales
    c_inv = dbc.Card(dbc.CardBody([html.H6("Inversión en Periodo"), html.H3(f"${inv:,.2f}")]), color="primary", outline=True)
    c_ben = dbc.Card(dbc.CardBody([html.H6("Impacto Social"), html.H3(f"{ben:,} hab")]), color="success", outline=True)
    c_reg = dbc.Card(dbc.CardBody([html.H6("Acciones"), html.H3(f"{len(df)}")]), color="dark", outline=True)

    fig_p = px.pie(df, names='tipo_de_servicio', hole=.4, title="Mix de Actividades")
    fig_b = px.bar(df.groupby('fecha_de_reporte', observed=True).size().reset_index(name='c'), 
                   x='fecha_de_reporte', y='c', title="Progreso Mensual", color_discrete_sequence=['#691c32'])

    tabla = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i.upper(), "id": i} for i in ['id', 'tipo_de_servicio', 'ubicacion_o_localidad', 'fecha_de_reporte', 'observaciones']],
        page_size=10, style_table={'overflowX': 'auto'}
    )

    return c_inv, c_ben, c_reg, fig_p, fig_b, tabla
