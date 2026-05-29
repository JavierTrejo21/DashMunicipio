import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

def cargar_datos_juridico():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM juridico", conn)
    conn.close()
    return df

def layout_juridico():
    return html.Div([
        html.H2("⚖️ 5.2 UNIDAD JURÍDICA - PANEL ESTRATÉGICO", style={'color': '#691c32', 'fontWeight': 'bold'}),
        html.Hr(),

        # --- FILTROS ---
        dbc.Row([
            dbc.Col([
                html.Label("Año:", className="fw-bold"),
                dcc.Dropdown(id='jur-anio', options=['2025', '2026'], value='2026', clearable=False)
            ], md=2),
            dbc.Col([
                html.Label("Trimestre:", className="fw-bold"),
                dcc.Dropdown(id='jur-trim', options=['1er Trimestre', '2do Trimestre', '3er Trimestre', '4to Trimestre'], multi=True, placeholder="Todos los trimestres")
            ], md=5),
            dbc.Col([
                html.Label("Mes:", className="fw-bold"),
                dcc.Dropdown(id='jur-mes', options=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'], multi=True, placeholder="Seleccionar meses")
            ], md=5),
        ], className="mb-4 p-3 bg-white shadow-sm rounded"),

        # --- TARJETAS DE INDICADORES ---
        dbc.Row([
            dbc.Col(id='uj-card-total-asesorias', md=4),
            dbc.Col(id='uj-card-convenios', md=4),
            dbc.Col(id='uj-card-localidades', md=4),
        ], className="mb-4"),

        # --- GRÁFICAS IMPACTANTES ---
        dbc.Row([
            # Gráfica 1: Composición de Asesorías
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("DISTRIBUCIÓN POR MATERIA JURÍDICA", className="fw-bold"),
                    dbc.CardBody([dcc.Graph(id='graph-materias', config={'displayModeBar': False})])
                ], className="shadow-sm h-100")
            ], md=6),
            
            # Gráfica 2: Trámites Técnicos y Administrativos
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("REVISIÓN DE DOCUMENTOS Y DESLINDES", className="fw-bold"),
                    dbc.CardBody([dcc.Graph(id='graph-tramites', config={'displayModeBar': False})])
                ], className="shadow-sm h-100")
            ], md=6),
        ], className="mb-4"),

        # --- TABLA DETALLADA ---
        dbc.Card([
            dbc.CardHeader("REGISTRO DETALLADO DE ATENCIONES", className="bg-dark text-white"),
            dbc.CardBody([
                html.Div(id='uj-tabla-container')
            ])
        ], className="shadow-sm mb-5")
    ], className="p-3")

@callback(
    [Output('uj-card-total-asesorias', 'children'), 
     Output('uj-card-convenios', 'children'), 
     Output('uj-card-localidades', 'children'),
     Output('graph-materias', 'figure'),
     Output('graph-tramites', 'figure'),
     Output('uj-tabla-container', 'children')],
    [Input('jur-anio', 'value'), Input('jur-trim', 'value'), Input('jur-mes', 'value')]
)
def actualizar_dashboard_juridico(anio, trim, mes):
    df = cargar_datos_juridico()
    
    if anio: df = df[df['anio'] == anio]
    if trim: df = df[df['trimestre'].isin(trim)]
    if mes:  df = df[df['mes'].isin(mes)]

    # --- LÓGICA DE DATOS ---
    # 1. Tarjetas
    cols_asesoria = ['asesoria_tenencia', 'asesoria_civil_familiar', 'juicios_obras', 'canalizaciones_pension']
    total_as = df[cols_asesoria].sum().sum()
    total_conv = df['convenios_contratos'].sum()
    total_loc = df['localidad'].nunique()

    # 2. Gráfica de Materias (Donut)
    materias_sum = df[cols_asesoria].sum().reset_index()
    materias_sum.columns = ['Materia', 'Total']
    materias_sum['Materia'] = materias_sum['Materia'].str.replace('_', ' ').str.title()
    fig_materias = px.pie(materias_sum, values='Total', names='Materia', hole=.4,
                          color_discrete_sequence=px.colors.qualitative.Antique)
    fig_materias.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", y=-0.1))

    # 3. Gráfica de Trámites (Barras Horizontales)
    cols_tramites = ['actas_registro_civil', 'revision_padron', 'traslados_dominio', 'revision_avaluos', 'deslindes_area']
    tramites_sum = df[cols_tramites].sum().sort_values(ascending=True).reset_index()
    tramites_sum.columns = ['Trámite', 'Cantidad']
    tramites_sum['Trámite'] = tramites_sum['Trámite'].str.replace('_', ' ').str.title()
    fig_tramites = px.bar(tramites_sum, x='Cantidad', y='Trámite', orientation='h',
                          color_discrete_sequence=['#bc955c'])
    fig_tramites.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_title=None, yaxis_title=None)

    # --- COMPONENTES VISUALES ---
    def generar_tarjeta(titulo, valor, color):
        return dbc.Card([
            dbc.CardBody([
                html.H6(titulo, className="card-title text-muted mb-0"),
                html.H2(valor, style={'color': '#212529', 'fontWeight': 'bold'})
            ])
        ], style={'borderLeft': f'6px solid {color}'}, className="shadow-sm text-center border-0")

    card1 = generar_tarjeta("Asesorías Totales", f"{int(total_as):,}", "#691c32")
    card2 = generar_tarjeta("Convenios/Contratos", f"{int(total_conv):,}", "#bc955c")
    card3 = generar_tarjeta("Localidades", f"{total_loc}", "#2d2d2d")

    tabla = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i.replace('_', ' ').upper(), "id": i} for i in df.columns if i not in ['id', 'anio', 'trimestre']],
        page_size=8,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontSize': '11px', 'fontWeight': 'bold'},
        style_cell={'fontSize': '11px', 'textAlign': 'left', 'padding': '10px'},
        filter_action="native"
    )
    
    return card1, card2, card3, fig_materias, fig_tramites, tabla
