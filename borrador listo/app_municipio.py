import dash
from dash import dcc, html, Input, Output, ALL, dash_table
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import json

# IMPORTANTE: Importamos las funciones de tu dashboard original
# Asegúrate de que dashboard.py esté en la misma carpeta
import dashboard 

# === 1. CONFIGURACIÓN ===
DB_GESTION = 'gestion_municipal.db'

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True) # Necesario para cargar contenido dinámico

# === 2. DISEÑO (LAYOUT) ===
app.layout = dbc.Container([
    # Encabezado Único
    dbc.Row([
        dbc.Col([
            html.H1("SISTEMA ESTRATÉGICO DE GESTIÓN MUNICIPAL", 
                    className="text-center my-4 text-primary font-weight-bold"),
            html.Hr(style={"borderTop": "3px solid #bc955c"})
        ], width=12)
    ]),
    
    # SECCIÓN SUPERIOR: TARJETAS DE ACUERDOS
    dbc.Row(id='contenedor-tarjetas-acuerdos', className="g-3 mb-4 justify-content-center"),
    
    # SECCIÓN INTERMEDIA: DESPLIEGUE DE ÁREAS
    dbc.Collapse(
        dbc.Card([
            dbc.CardHeader(id="titulo-acuerdo-dinamico", className="bg-primary text-white font-weight-bold"),
            dbc.CardBody(id='selector-areas-acuerdo')
        ], className="shadow-sm mb-5"),
        id="collapse-areas", is_open=False
    ),
    
    # SECCIÓN INFERIOR: AQUÍ SE MOSTRARÁ TU DASHBOARD.PY
    html.Div(id='contenedor-dashboard-real')

], fluid=True)

# === 3. CALLBACKS DE NAVEGACIÓN ===

# Renderiza las tarjetas de acuerdos desde la BD de gestión
@app.callback(
    Output('contenedor-tarjetas-acuerdos', 'children'),
    Input('contenedor-tarjetas-acuerdos', 'id')
)
def cargar_acuerdos(_):
    conn = sqlite3.connect(DB_GESTION)
    df_ac = pd.read_sql_query("SELECT * FROM acuerdos", conn)
    conn.close()
    
    iconos = ["bi-people", "bi-heart-pulse", "bi-book", "bi-building-gear", "bi-shield-check", "bi-cpu", "bi-eye"]
    
    return [
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.I(className=f"{iconos[i%7]} h2 text-primary mb-2"),
                html.H6(row['nombre'], className="text-center font-weight-bold", style={"fontSize": "0.7rem", "height":"40px"}),
                dbc.Button("Explorar", id={'type': 'btn-acuerdo', 'index': row['id']}, color="primary", size="sm", className="w-100 mt-2")
            ], className="d-flex flex-column align-items-center")
        ], className="h-100 shadow-sm border-0 border-top border-primary border-4"), md=2) 
        for i, row in df_ac.iterrows()
    ]

# Despliega las áreas al hacer clic en un acuerdo
@app.callback(
    [Output("collapse-areas", "is_open"), 
     Output("selector-areas-acuerdo", "children"),
     Output("titulo-acuerdo-dinamico", "children")],
    Input({'type': 'btn-acuerdo', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def mostrar_areas(n):
    if not dash.callback_context.triggered or not any(n): return False, "", ""
    
    # Obtener ID del acuerdo clicado
    acuerdo_id = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])['index']
    
    conn = sqlite3.connect(DB_GESTION)
    df_areas = pd.read_sql_query(f"SELECT * FROM areas WHERE acuerdo_id = {acuerdo_id}", conn)
    ac_nom = pd.read_sql_query(f"SELECT nombre FROM acuerdos WHERE id = {acuerdo_id}", conn).iloc[0]['nombre']
    conn.close()
    
    botones = [
        dbc.Button(f"{r['codigo_informe']} {r['nombre']}", 
                   id={'type': 'btn-area', 'index': r['id']},
                   color="dark", outline=True, className="m-1 btn-sm shadow-sm") 
        for _, r in df_areas.iterrows()
    ]
    
    return True, botones, f"Eje Estratégico: {ac_nom}"

# MUESTRA EL CONTENIDO DE DASHBOARD.PY
@app.callback(
    Output('contenedor-dashboard-real', 'children'),
    Input({'type': 'btn-area', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def inyectar_dashboard(n):
    if not any(n): return ""
    
    # Obtenemos el ID del área para saber si es 4.5 (Obras Públicas)
    area_id = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])['index']
    
    conn = sqlite3.connect(DB_GESTION)
    area_info = pd.read_sql_query(f"SELECT * FROM areas WHERE id = {area_id}", conn).iloc[0]
    conn.close()

    if area_info['codigo_informe'] == '4.5':
        # AQUÍ ESTÁ EL TRUCO: 
        # Llamamos a la estructura de dashboard.py pero sin los filtros superiores 
        # para que no choquen con tu nuevo menú.
        
        df = dashboard.cargar_datos() # Usamos la función de carga de dashboard.py
        
        # Reutilizamos tu lógica de indicadores y gráficas de dashboard.py
        indicadores, fig_estatus, fig_top_loc, tabla_data = dashboard.filtrar_dashboard(None, None)
        
        return html.Div([
            html.Div(indicadores, style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_estatus), md=6),
                dbc.Col(dcc.Graph(figure=fig_top_loc), md=6)
            ]),
            html.Div([
                html.H3("Cédula de Información de Obra Pública", className="mt-4 text-primary"),
                dash_table.DataTable(
                    data=tabla_data,
                    columns=[{"name": i.upper(), "id": i} for i in df.columns],
                    page_size=10,
                    style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontWeight': 'bold'},
                    style_cell={'padding': '10px'}
                )
            ])
        ], className="animate__animated animate__fadeIn")

    return dbc.Alert(f"El módulo {area_info['nombre']} está configurado, pero no tiene un dashboard asignado aún.", color="info")

if __name__ == '__main__':
    app.run(debug=True, port=8050)
