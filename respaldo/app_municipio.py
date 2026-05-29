import dash
from dash import dcc, html, Input, Output, ALL, dash_table, State
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import json

# === 1. IMPORTACIÓN DE MÓDULOS DE ÁREA ===
# Es vital que estos archivos existan en tu carpeta C:\DashMunicipio
try:
    import dashboard  # Obra Pública (Usa tabla 'proyectos')
    import juridico   # Unidad Jurídica
    import atencion   # Atención Ciudadana
    import comude     # Deporte
    import servicios  # Servicios Públicos (Usa tu archivo servicios.py)
except ImportError as e:
    print(f"⚠️ Error de importación: {e}")

# === 2. CONFIGURACIÓN ===
DB_GESTION = 'gestion_municipal.db'

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True)

# === 3. DISEÑO (LAYOUT) ===
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("SISTEMA ESTRATÉGICO DE GESTIÓN MUNICIPAL", 
                    className="text-center my-4 text-primary font-weight-bold"),
            html.Hr(style={"borderTop": "3px solid #bc955c"})
        ], width=12)
    ]),
    
    dbc.Row(id='contenedor-tarjetas-acuerdos', className="g-3 mb-4 justify-content-center"),
    
    dbc.Collapse(
        dbc.Card([
            dbc.CardHeader(id='titulo-acuerdo-seleccionado', className="bg-primary text-white font-weight-bold"),
            dbc.CardBody(id='contenedor-botones-areas', className="d-flex flex-wrap justify-content-center")
        ], className="shadow-sm mb-4"),
        id="collapse-areas", is_open=False,
    ),
    
    html.Div(id='contenido-area', className="mt-4")
], fluid=True, style={'backgroundColor': '#f4f4f4', 'minHeight': '100vh'})

# === 4. CALLBACKS ===

@app.callback(
    Output('contenedor-tarjetas-acuerdos', 'children'),
    Input('contenedor-tarjetas-acuerdos', 'id')
)
def cargar_acuerdos(_):
    conn = sqlite3.connect(DB_GESTION)
    df_ac = pd.read_sql_query("SELECT * FROM acuerdos", conn)
    conn.close()
    return [
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5(fila['nombre'], className="card-title text-center small font-weight-bold"),
                dbc.Button("Explorar", id={'type': 'btn-acuerdo', 'index': fila['id']}, 
                           color="primary", size="sm", className="w-100")
            ])
        ], className="h-100 shadow-sm border-0", style={"borderTop": "4px solid #691c32"}),
        width=6, md=2) for _, fila in df_ac.iterrows()
    ]

@app.callback(
    [Output('collapse-areas', 'is_open'),
     Output('titulo-acuerdo-seleccionado', 'children'),
     Output('contenedor-botones-areas', 'children')],
    [Input({'type': 'btn-acuerdo', 'index': ALL}, 'n_clicks')],
    [State({'type': 'btn-acuerdo', 'index': ALL}, 'id')]
)
def desplegar_areas(n_clicks, ids):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None):
        return False, "", ""
    id_ac = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    conn = sqlite3.connect(DB_GESTION)
    nombre_ac = pd.read_sql_query(f"SELECT nombre FROM acuerdos WHERE id={id_ac}", conn).iloc[0]['nombre']
    df_areas = pd.read_sql_query(f"SELECT * FROM areas WHERE acuerdo_id={id_ac}", conn)
    conn.close()
    botones = [dbc.Button(a['nombre'], id={'type': 'btn-area', 'index': a['id']}, color="outline-primary", className="m-2 shadow-sm")
               for _, a in df_areas.iterrows()]
    return True, f"ÁREAS DE: {nombre_ac}", botones

@app.callback(
    Output('contenido-area', 'children'),
    [Input({'type': 'btn-area', 'index': ALL}, 'n_clicks')],
    [State({'type': 'btn-area', 'index': ALL}, 'id')]
)
def mostrar_dashboard(n_clicks, ids):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None):
        return ""
    
    id_area = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    conn = sqlite3.connect(DB_GESTION)
    area_info = pd.read_sql_query(f"SELECT nombre FROM areas WHERE id={id_area}", conn).iloc[0]
    conn.close()
    
    # Normalización para que no fallen acentos ni espacios
    nombre_clean = area_info['nombre'].upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').strip()

    # --- RUTEADOR DE MÓDULOS ---

    # 1. OBRA PÚBLICA
    if "OBRA" in nombre_clean or "PROYECTO" in nombre_clean:
        try:
            df_obras = dashboard.cargar_datos()
            ind, f1, f2, data = dashboard.filtrar_dashboard(None, None)
            return html.Div([
                html.H2(f"📑 {area_info['nombre']}", className="text-primary mb-4"),
                html.Div(ind, style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
                dbc.Row([dbc.Col(dcc.Graph(figure=f1), md=6), dbc.Col(dcc.Graph(figure=f2), md=6)]),
                dash_table.DataTable(data=data, columns=[{"name": i.upper(), "id": i} for i in df_obras.columns],
                                     page_size=10, style_header={'backgroundColor': '#691c32', 'color': 'white'},
                                     style_table={'overflowX': 'auto'})
            ])
        except Exception as e: return dbc.Alert(f"Error en Obras: {e}", color="danger")

    # 2. UNIDAD JURÍDICA
    elif "JURIDICA" in nombre_clean:
        return juridico.layout_juridico()

    # 3. ATENCIÓN CIUDADANA
    elif "ATENCION" in nombre_clean:
        return atencion.layout_atencion()

    # 4. COMUDE / DEPORTE
    elif "COMUDE" in nombre_clean or "DEPORTE" in nombre_clean:
        return comude.layout_comude()
    # 5. SERVICIOS PÚBLICOS
    elif "SERVICIOS" in nombre_clean:
        try:
            import servicios # Importamos aquí para asegurar que Python lo reconozca
            return servicios.layout_servicios()
        except Exception as e:
            return dbc.Alert(f"Error al cargar el módulo de Servicios: {e}", color="danger")

if __name__ == "__main__":
    app.run(debug=True, port=8050)
