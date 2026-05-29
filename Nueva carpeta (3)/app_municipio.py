import dash
from dash import dcc, html, Input, Output, ALL, dash_table, State, no_update
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import json
from io import StringIO

from database import inicializar_db, normalizar_nombre_tabla, DB_GESTION
from layouts import servir_layout

inicializar_db()

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP], 
                suppress_callback_exceptions=True)

app.layout = servir_layout()

# --- FUNCIONES AUXILIARES ---
def crear_kpi_card(titulo, valor, color, icono):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className=f"{icono} me-2"),
                    html.Span(titulo, className="text-muted small font-weight-bold")
                ], className="d-flex align-items-center mb-2"),
                html.H3(valor, className=f"text-{color} font-weight-bold mb-0")
            ])
        ], className="shadow-sm border-start border-4", style={"borderLeftColor": f"var(--bs-{color}) !important"}),
        md=4
    )

# --- CALLBACKS DE NAVEGACIÓN ---

@app.callback(
    Output('contenedor-tarjetas-acuerdos', 'children'),
    Input('contenedor-tarjetas-acuerdos', 'id')
)
def cargar_acuerdos(_):
    conn = sqlite3.connect(DB_GESTION)
    df = pd.read_sql_query("SELECT * FROM acuerdos", conn)
    conn.close()
    return [dbc.Col(dbc.Card(dbc.CardBody([
        html.H5(f['nombre'], className="text-center small font-weight-bold"),
        dbc.Button("Seleccionar", id={'type': 'btn-acuerdo', 'index': f['id']}, color="primary", size="sm", className="w-100")
    ])), width=6, md=2) for _, f in df.iterrows()]

@app.callback(
    [Output('collapse-areas', 'is_open'), Output('titulo-acuerdo-seleccionado', 'children'), Output('contenedor-botones-areas', 'children')],
    [Input({'type': 'btn-acuerdo', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def desplegar_areas(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None): return False, "", ""
    idx = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    conn = sqlite3.connect(DB_GESTION)
    df = pd.read_sql_query(f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn)
    conn.close()
    botones = [dbc.Button(a['nombre'], id={'type': 'btn-area', 'index': a['id']}, color="outline-primary", className="m-2") for _, a in df.iterrows()]
    return True, "ÁREAS DEL ACUERDO ESTRATÉGICO", botones

@app.callback(
    [Output('contenido-area', 'children'), 
     Output('active-info', 'data'),
     Output('resumen-kpis', 'children')],
    [Input({'type': 'btn-area', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def mostrar_dashboard(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None): return "", no_update, ""
    
    idx = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    conn = sqlite3.connect(DB_GESTION)
    area = pd.read_sql_query("SELECT id, nombre FROM areas WHERE id=?", conn, params=(idx,)).iloc[0]
    tabla = normalizar_nombre_tabla(area['nombre'])
    info_store = {'tabla': tabla, 'id': int(area['id'])}
    
    try:
        df = pd.read_sql_query(f"SELECT rowid, * FROM {tabla}", conn)
        conn.close()

        # Cálculo de KPIs (Inversión y Beneficiarios)
        kpis = []
        col_inv = [c for c in df.columns if 'INVERSION' in c.upper()]
        col_ben = [c for c in df.columns if 'BENEFICIARIO' in c.upper()]

        total_inv = pd.to_numeric(df[col_inv[0]], errors='coerce').sum() if col_inv else 0
        total_ben = pd.to_numeric(df[col_ben[0]], errors='coerce').sum() if col_ben else 0

        kpis.append(crear_kpi_card("INVERSIÓN TOTAL", f"${total_inv:,.2f}", "success", "bi bi-cash-stack"))
        kpis.append(crear_kpi_card("TOTAL BENEFICIARIOS", f"{int(total_ben):,}", "info", "bi bi-people"))
        kpis.append(crear_kpi_card("ACCIONES REGISTRADAS", len(df), "primary", "bi bi-clipboard-data"))

        fila_resumen = dbc.Row(kpis, className="mb-4")

        # Tabla
        layout_tabla = html.Div([
            dbc.Row([
                dbc.Col(html.H2(f"📊 {area['nombre']}", className="text-primary"), md=9),
                dbc.Col(dbc.Button("💾 GUARDAR CAMBIOS", id="btn-save", color="success", className="w-100"), md=3)
            ], className="mb-3 align-items-center"),
            html.Div(id='notif-area'),
            dash_table.DataTable(
                id='main-table', data=df.to_dict('records'),
                columns=[{"name": i.upper(), "id": i, "editable": (i != 'rowid')} for i in df.columns],
                row_deletable=True, page_size=15, editable=True, filter_action="native",
                style_header={'backgroundColor': '#691c32', 'color': 'white'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_table={'overflowX': 'auto'}
            )
        ])
        return layout_tabla, info_store, fila_resumen
    except:
        return dbc.Alert("Esta área no contiene datos.", color="warning"), info_store, ""

# --- CALLBACKS DE GESTIÓN ---

@app.callback(
    [Output("modal-config", "is_open"), Output("modal-update", "is_open"), Output("modal-borrado-admin", "is_open"),
     Output("update-area-selector", "options"), Output("borrar-area-selector", "options")],
    [Input("btn-abrir-config", "n_clicks"), Input("btn-abrir-update", "n_clicks"), 
     Input("btn-abrir-borrado-seccion", "n_clicks"), Input("btn-cerrar-borrado", "n_clicks")],
    [State("modal-config", "is_open"), State("modal-update", "is_open"), State("modal-borrado-admin", "is_open")],
    prevent_initial_call=True
)
def ctrl_modales(n1, n2, n3, n4, s1, s2, s3):
    ctx = dash.callback_context
    btn = ctx.triggered[0]['prop_id'].split('.')[0]
    opts = []
    if btn in ["btn-abrir-update", "btn-abrir-borrado-seccion"]:
        conn = sqlite3.connect(DB_GESTION)
        df = pd.read_sql_query("SELECT id, nombre FROM areas", conn)
        conn.close()
        opts = [{'label': r['nombre'], 'value': r['id']} for _, r in df.iterrows()]

    if btn == "btn-abrir-config": return True, False, False, [], []
    if btn == "btn-abrir-update": return False, True, False, opts, []
    if btn == "btn-abrir-borrado-seccion": return False, False, True, [], opts
    return False, False, False, [], []

@app.callback(
    Output("notif-area", "children"),
    Input("btn-save", "n_clicks"),
    [State("main-table", "data"), State("active-info", "data")],
    prevent_initial_call=True
)
def save_data(n, rows, info):
    df = pd.DataFrame(rows)
    if 'rowid' in df.columns: df = df.drop(columns=['rowid'])
    conn = sqlite3.connect(DB_GESTION)
    df.to_sql(info['tabla'], conn, if_exists='replace', index=False)
    conn.close()
    return dbc.Alert("✅ Base de datos actualizada.", color="success", duration=2000)

@app.callback(
    Output("update-status", "children"),
    Input("btn-update-validar", "n_clicks"),
    [State("update-area-selector", "value"), State("update-texto-excel", "value")],
    prevent_initial_call=True
)
def append_rows(n, a_id, txt):
    if not a_id or not txt: return "Error: Faltan datos"
    conn = sqlite3.connect(DB_GESTION)
    area = pd.read_sql_query("SELECT nombre FROM areas WHERE id=?", conn, params=(a_id,)).iloc[0]
    df = pd.read_csv(StringIO(txt), sep='\t').map(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_sql(normalizar_nombre_tabla(area['nombre']), conn, if_exists='append', index=False)
    conn.close()
    return dbc.Alert(f"✅ Filas añadidas a {area['nombre']}", color="success")

@app.callback(
    Output("borrar-status", "children"),
    Input("btn-confirmar-borrado-final", "n_clicks"),
    State("borrar-area-selector", "value"),
    prevent_initial_call=True
)
def delete_area(n, a_id):
    if not a_id: return "Selecciona un área."
    conn = sqlite3.connect(DB_GESTION)
    area = pd.read_sql_query("SELECT nombre FROM areas WHERE id=?", conn, params=(a_id,)).iloc[0]
    conn.execute(f"DROP TABLE IF EXISTS {normalizar_nombre_tabla(area['nombre'])}")
    conn.execute("DELETE FROM areas WHERE id=?", (a_id,))
    conn.commit(); conn.close()
    return dbc.Alert(f"🗑️ Área eliminada. Refresca con F5.", color="warning")

@app.callback(
    Output("salida-confirmacion", "children"),
    Input("btn-guardar-excel", "n_clicks"),
    [State("input-nombre-area", "value"), State("input-acuerdo-id", "value"), State("area-texto-excel", "value")],
    prevent_initial_call=True
)
def create_new(n, nom, ac, txt):
    if not nom or not txt: return "Error"
    df = pd.read_csv(StringIO(txt), sep='\t').map(lambda x: x.strip() if isinstance(x, str) else x)
    conn = sqlite3.connect(DB_GESTION)
    df.to_sql(normalizar_nombre_tabla(nom), conn, if_exists='replace', index=False)
    conn.execute("INSERT INTO areas (nombre, acuerdo_id) VALUES (?, ?)", (nom.upper(), ac))
    conn.commit(); conn.close()
    return dbc.Alert("✅ Nueva área creada.", color="success")

if __name__ == "__main__":
    app.run(debug=True, port=8050)
