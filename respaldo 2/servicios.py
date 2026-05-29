import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

def cargar_datos():
    conn = sqlite3.connect('municipio.db')
    # Cargamos la tabla servicios_publicos
    df = pd.read_sql_query("SELECT * FROM servicios_publicos", conn)
    conn.close()
    
    # --- LIMPIEZA DE COLUMNAS ---
    # Esto elimina espacios raros o puntos que puedan venir de la DB
    df.columns = [c.strip().lower().replace(' ', '_').replace('.', '') for c in df.columns]

    # 1. Limpieza de Inversión (Aseguramos que materiales_utilizados sea número si ahí guardas costos)
    # Si materiales_utilizados es texto, intentamos convertirlo
    df['inversion_num'] = pd.to_numeric(df['materiales_utilizados'], errors='coerce').fillna(0)
    
    # 2. Extracción de Beneficiarios (Buscamos el número en la columna observaciones)
    df['beneficiarios_num'] = df['observaciones'].astype(str).str.extract(r'(\d+)').astype(float).fillna(0)
    
    # 3. Lógica de Trimestres
    mapa_trimestres = {
        'ENERO': '1er Trimestre', 'FEBRERO': '1er Trimestre', 'MARZO': '1er Trimestre',
        'ABRIL': '2do Trimestre', 'MAYO': '2do Trimestre', 'JUNIO': '2do Trimestre',
        'JULIO': '3er Trimestre', 'AGOSTO': '3er Trimestre', 'SEPTIEMBRE': '3er Trimestre',
        'OCTUBRE': '4to Trimestre', 'NOVIEMBRE': '4to Trimestre', 'DICIEMBRE': '4to Trimestre'
    }
    # Usamos la columna fecha_de_reporte (ya normalizada a minúsculas por la limpieza de arriba)
    df['trimestre'] = df['fecha_de_reporte'].str.upper().map(mapa_trimestres).fillna('Sin Clasificar')
    df['anio'] = "2026" 
    
    return df

def layout_servicios():
    try:
        df = cargar_datos()
    except Exception as e:
        return dbc.Alert(f"Error al cargar datos: {e}", color="danger")
    
    return html.Div([
        html.H2("📊 CONTROL DE AVANCES: SERVICIOS PÚBLICOS", 
                style={'color': '#691c32', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Hr(style={'borderTop': '3px solid #bc955c'}),

        # --- FILTROS ---
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("📅 Año:"),
                        dcc.Dropdown(id='f-anio', options=['2025', '2026'], value='2026', clearable=False)
                    ], md=4),
                    dbc.Col([
                        html.Label("⏱️ Trimestre:"),
                        dcc.Dropdown(id='f-trimestre', 
                                   options=[{'label': t, 'value': t} for t in ['1er Trimestre', '2do Trimestre', '3er Trimestre', '4to Trimestre']],
                                   multi=True)
                    ], md=4),
                    dbc.Col([
                        html.Label("📆 Mes:"),
                        dcc.Dropdown(id='f-mes', options=[{'label': m, 'value': m} for m in df['fecha_de_reporte'].unique()], multi=True)
                    ], md=4),
                ])
            ])
        ], className="mb-4 shadow-sm"),

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

@callback(
    [Output('kpi-inv', 'children'), Output('kpi-ben', 'children'), Output('kpi-reg', 'children'),
     Output('graph-pie', 'figure'), Output('graph-bar', 'figure'), Output('table-container', 'children')],
    [Input('f-anio', 'value'), Input('f-trimestre', 'value'), Input('f-mes', 'value')]
)
def filtrar_todo(anio, trim, mes):
    df = cargar_datos()

    # Filtros
    if anio: df = df[df['anio'] == anio]
    if trim: df = df[df['trimestre'].isin(trim)]
    if mes:  df = df[df['fecha_de_reporte'].isin(mes)]

    # Datos para KPIs
    inv = df['inversion_num'].sum()
    ben = int(df['beneficiarios_num'].sum())
    
    c_inv = dbc.Card(dbc.CardBody([html.H6("Inversión"), html.H3(f"${inv:,.2f}")]), color="primary", outline=True)
    c_ben = dbc.Card(dbc.CardBody([html.H6("Beneficiarios"), html.H3(f"{ben:,}")]), color="success", outline=True)
    c_reg = dbc.Card(dbc.CardBody([html.H6("Registros"), html.H3(f"{len(df)}")]), color="dark", outline=True)

    # Gráficas (Asegúrate que los nombres de columnas coincidan con tu DB)
    # Si tu columna se llama 'tipo_de_servicio' en la DB, tras la limpieza es 'tipo_de_servicio'
    fig_p = px.pie(df, names='tipo_de_servicio', hole=.4, title="Distribución por Servicio")
    fig_b = px.bar(df.groupby('fecha_de_reporte').size().reset_index(name='cuenta'), 
                   x='fecha_de_reporte', y='cuenta', title="Actividad Mensual")

    # Tabla: Mostramos todas las columnas disponibles para verificar
    tabla = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i.upper(), "id": i} for i in df.columns if i not in ['inversion_num', 'beneficiarios_num', 'anio', 'trimestre']],
        page_size=10,
        style_table={'overflowX': 'auto'}
    )

    return c_inv, c_ben, c_reg, fig_p, fig_b, tabla
