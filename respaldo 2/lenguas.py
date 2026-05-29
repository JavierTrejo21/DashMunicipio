import pandas as pd
import sqlite3
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

def cargar_datos():
    conn = sqlite3.connect('municipio.db')
    df = pd.read_sql_query("SELECT * FROM lenguas_indigenas", conn)
    conn.close()
    
    # 1. Limpieza de nombres de columnas
    df.columns = [c.strip() for c in df.columns]
    
    # 2. LIMPIEZA RADICAL: Forzamos a que todo sea texto y reemplazamos nulos
    # Esto elimina la raíz del error '<' entre float y str
    cols_a_limpiar = ['MES', 'Barrio/Localidad', 'PROGRAMA / TIPO DE APOYO', 'Comunidades indígenas que hablan lengua materna']
    for col in cols_a_limpiar:
        if col in df.columns:
            # Convertimos a string, quitamos espacios y evitamos el valor 'nan' de float
            df[col] = df[col].astype(str).replace(['nan', 'None', 'NAN', 'nan ', ''], 'SIN DATO').str.strip()
    
    # 3. Lógica de Trimestres
    mapa_trimestres = {
        'ENERO': '1er Trimestre', 'FEBRERO': '1er Trimestre', 'MARZO': '1er Trimestre',
        'ABRIL': '2do Trimestre', 'MAYO': '2do Trimestre', 'JUNIO': '2do Trimestre',
        'JULIO': '3er Trimestre', 'AGOSTO': '3er Trimestre', 'SEPTIEMBRE': '3er Trimestre',
        'OCTUBRE': '4to Trimestre', 'NOVIEMBRE': '4to Trimestre', 'DICIEMBRE': '4to Trimestre'
    }
    df['TRIMESTRE'] = df['MES'].str.upper().map(mapa_trimestres).fillna('Sin Clasificar')
    
    # 4. Números seguros
    df['BENEFICIARIOS'] = pd.to_numeric(df['BENEFICIARIOS'], errors='coerce').fillna(0)
    df['INVERSION'] = pd.to_numeric(df['INVERSION'], errors='coerce').fillna(0)
    
    return df

def layout_lenguas():
    try:
        df = cargar_datos()
        
        # Generamos las listas de opciones asegurando que TODO sea string antes del sorted()
        def obtener_opciones(columna):
            valores = [str(x) for x in df[columna].unique() if x is not None]
            return [{'label': i, 'value': i} for i in sorted(valores)]

        opt_mes = obtener_opciones('MES')
        opt_loc = obtener_opciones('Barrio/Localidad')
        opt_prog = obtener_opciones('PROGRAMA / TIPO DE APOYO')
        
    except Exception as e:
        return dbc.Alert(f"Error crítico en datos: {e}", color="danger")
    
    return html.Div([
        html.H2("5.1.3 LENGUAS INDÍGENAS", 
                style={'color': '#691c32', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Hr(style={'borderTop': '3px solid #bc955c'}),

        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("⏱️ Trimestre:"),
                        dcc.Dropdown(
                            id='f-trim-len', 
                            options=[{'label': t, 'value': t} for t in ['1er Trimestre', '2do Trimestre', '3er Trimestre', '4to Trimestre']],
                            multi=True
                        )
                    ], md=3),
                    dbc.Col([html.Label("📆 Mes:"), dcc.Dropdown(id='f-mes-len', options=opt_mes, multi=True)], md=3),
                    dbc.Col([html.Label("📍 Localidad:"), dcc.Dropdown(id='f-loc-len', options=opt_loc, multi=True)], md=3),
                    dbc.Col([html.Label("🎁 Programa:"), dcc.Dropdown(id='f-prog-len', options=opt_prog, multi=True)], md=3),
                ])
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Row([
            dbc.Col(id='kpi-len-ben', md=4),
            dbc.Col(id='kpi-len-inv', md=4),
            dbc.Col(id='kpi-len-acc', md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-len-pie'), md=6),
            dbc.Col(dcc.Graph(id='graph-len-bar'), md=6),
        ]),

        html.Div(id='table-len-container', className="mt-4")
    ], className="p-4")

@callback(
    [Output('kpi-len-ben', 'children'), Output('kpi-len-inv', 'children'), Output('kpi-len-acc', 'children'),
     Output('graph-len-pie', 'figure'), Output('graph-len-bar', 'figure'), Output('table-len-container', 'children')],
    [Input('f-trim-len', 'value'), Input('f-mes-len', 'value'), Input('f-loc-len', 'value'), Input('f-prog-len', 'value')]
)
def filtrar_todo(trim, mes, loc, prog):
    df = cargar_datos()

    if trim: df = df[df['TRIMESTRE'].isin(trim)]
    if mes:  df = df[df['MES'].isin(mes)]
    if loc:  df = df[df['Barrio/Localidad'].isin(loc)]
    if prog: df = df[df['PROGRAMA / TIPO DE APOYO'].isin(prog)]

    ben = int(df['BENEFICIARIOS'].sum())
    inv = df['INVERSION'].sum()
    
    c_ben = dbc.Card(dbc.CardBody([html.H6("Beneficiarios"), html.H3(f"{ben:,}")]), color="success", outline=True)
    c_inv = dbc.Card(dbc.CardBody([html.H6("Inversión"), html.H3(f"${inv:,.2f}")]), color="primary", outline=True)
    c_acc = dbc.Card(dbc.CardBody([html.H6("Acciones"), html.H3(f"{len(df)}")]), color="dark", outline=True)

    # Gráficas
    fig_p = px.pie(df, names='Comunidades indígenas que hablan lengua materna', title="Habla Lengua Materna", hole=.4)
    df_bar = df.groupby('Barrio/Localidad')['BENEFICIARIOS'].sum().nlargest(10).reset_index()
    fig_b = px.bar(df_bar, x='BENEFICIARIOS', y='Barrio/Localidad', orientation='h', title="Top 10 Localidades")

    tabla = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i.upper(), "id": i} for i in ['MES', 'Barrio/Localidad', 'BENEFICIARIOS', 'PROGRAMA / TIPO DE APOYO', 'INVERSION']],
        page_size=10, 
        style_table={'overflowX': 'auto'}
    )

    return c_ben, c_inv, c_acc, fig_p, fig_b, tabla
