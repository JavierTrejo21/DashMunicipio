import dash
from dash import dcc, html, Input, Output, callback
import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import os

if os.path.exists('gestion_municipal.db'):
    print("✅ ¡Archivo de base de datos encontrado!")
else:
    print("❌ No encuentro el archivo 'gestion_municipal.db' en esta carpeta.")
    print(f"Carpeta actual de trabajo: {os.getcwd()}")

# 1. Funciones de Base de Datos
def obtener_datos_gobierno():
    conn = sqlite3.connect('gestion_municipal.db')
    query = """
    SELECT ac.id as ac_id, ac.nombre AS nombre_acuerdo, a.id as area_id,
           a.codigo_informe, a.nombre AS nombre_area
    FROM areas a
    JOIN acuerdos ac ON a.acuerdo_id = ac.id
    ORDER BY ac.id, a.codigo_informe;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 2. Inicializar App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 3. Layout Principal
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Portal de Gestión Municipal", 
                        className="text-center my-4 text-primary font-weight-bold"), width=12)
    ]),
    
    # Sección de Tarjetas
    dbc.Row(id='contenedor-tarjetas', className="mb-5"),
    
    # Línea divisoria
    html.Hr(),
    
    # Sección de Detalle Dinámico (Aquí se cargará lo de Obras Públicas, etc.)
    dbc.Row([
        dbc.Col(id='detalle-area-contenido', width=12)
    ])
], fluid=True)

# 4. Callback para generar las tarjetas inicialmente
@app.callback(
    Output('contenedor-tarjetas', 'children'),
    Input('contenedor-tarjetas', 'id') # Se ejecuta al cargar
)
def renderizar_tarjetas(_):
    df = obtener_datos_gobierno()
    acuerdos = df['nombre_acuerdo'].unique()
    tarjetas = []

    for acuerdo in acuerdos:
        areas_acuerdo = df[df['nombre_acuerdo'] == acuerdo]
        
        lista_areas = html.Div([
            dbc.Button(
                f"{row['codigo_informe']} {row['nombre_area']}",
                id={'type': 'btn-area', 'index': row['area_id']},
                color="link",
                className="text-start p-1 w-100",
                style={"textDecoration": "none", "fontSize": "0.85rem"}
            ) for _, row in areas_acuerdo.iterrows()
        ])

        card = dbc.Col(
            dbc.Card([
                dbc.CardHeader(acuerdo, className="bg-dark text-white", style={"minHeight": "70px"}),
                dbc.CardBody(lista_areas, style={"height": "250px", "overflowY": "auto"}),
            ], className="shadow h-100"),
            xs=12, md=4, lg=3, className="mb-4"
        )
        tarjetas.append(card)
    return tarjetas

# 5. Callback para mostrar la información detallada del área seleccionada
@app.callback(
    Output('detalle-area-contenido', 'children'),
    Input({'type': 'btn-area', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def mostrar_detalle(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div("Seleccione un área para ver los detalles.", className="text-muted")
    
    # Obtener el ID del área presionada
    boton_id = ctx.triggered[0]['prop_id'].split('.')[0]
    import json
    area_id = json.loads(boton_id)['index']
    
    # Aquí es donde conectas con tus tablas de SQL previas (ejemplo Obras Públicas)
    # Por ahora, mostraremos un contenedor de ejemplo:
    return dbc.Card([
        dbc.CardHeader(f"Detalle Operativo - Área ID: {area_id}", className="bg-info text-white"),
        dbc.CardBody([
            html.H4("Indicadores de Desempeño y Presupuesto"),
            html.P("Cargando datos de SQL para el área seleccionada..."),
            # Aquí insertarías tus dcc.Graph() y dash_table.DataTable()
            dbc.Row([
                dbc.Col(dcc.Graph(figure=px.bar(title="Avance Físico vs Financiero")), width=6),
                dbc.Col(html.Div("Aquí va la tabla de códigos SQL trabajada anteriormente"), width=6)
            ])
        ])
    ], className="mt-3")

if __name__ == '__main__':
    app.run_server(debug=True)
