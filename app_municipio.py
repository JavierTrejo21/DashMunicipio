import dash
from dash import dcc, html, Input, Output, ALL, dash_table, State, no_update
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import json
from io import StringIO

# Módulos Locales
from database import inicializar_db, normalizar_nombre_tabla, DB_GESTION
from layouts import servir_layout
from visualizaciones import generar_tablero_impacto, seccion_impacto_layout
from indicadores_pbr import calcular_indicadores_pbr 

# --- DICCIONARIO DE DEFINICIONES ESTRATÉGICAS ---
DICCIONARIO_AREAS = {
    "5_1_1_RECEPCION_MUNICIPAL_PRESIDENTA": {
        "resumen": "Registro y control de las solicitudes ciudadanas, apoyos económicos y gestiones institucionales atendidas en la oficina de la Presidencia Municipal.",
        "objetivo": "Garantizar una atención ciudadana oportuna, transparente y de alto impacto social directa en las comunidades."
    }
}

DICCIONARIO_ICONOS_ACUERDOS = {
    1: "bi bi-handshake", 
    2: "bi bi-heart-pulse", 
    3: "bi bi-cash-coin", 
    4: "bi bi-lightbulb"
}

def obtener_url_csv(url_sheets):
    """Convierte link de compartir en link de descarga CSV para Pandas."""
    try:
        if "/edit" in url_sheets:
            base_url = url_sheets.split("/edit")[0]
            if "gid=" in url_sheets:
                gid = url_sheets.split("gid=")[1].split("&")[0]
                return f"{base_url}/export?format=csv&gid={gid}"
            return f"{base_url}/export?format=csv"
        return url_sheets
    except:
        return url_sheets

# Inicializar Base de Datos al arrancar
inicializar_db()

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP], 
    suppress_callback_exceptions=True
)

app.layout = servir_layout()

# --- TRADUCTOR COMPONENTE VISUAL PARA LOS INDICADORES PbR ---
def diseñar_tarjeta_pbr(datos_pbr):
    if not datos_pbr:
        return dbc.Alert("Esperando integración de datos...", color="light")
    if isinstance(datos_pbr, list):
        return dbc.Row(datos_pbr, className="mb-4")
    if isinstance(datos_pbr, dict):
        color_map = {"Verde": "success", "Amarillo": "warning", "Rojo": "danger", "Azul": "info"}
        color_alerta = color_map.get(datos_pbr.get('estatus_semaforo'), "light")
        return dbc.Alert([
            html.H5("🎯 EVALUACIÓN DE DESEMPEÑO INSTITUCIONAL (PbR)", className="alert-heading font-weight-bold", style={"fontSize": "0.9rem"}),
            html.Hr(style={"margin": "8px 0"}),
            dbc.Row([
                dbc.Col([
                    html.P(f"📊 Cumplimiento: {datos_pbr.get('porcentaje_cumplimiento', 0)}%", className="mb-1 font-weight-bold", style={"fontSize": "0.85rem"}),
                    html.P(f"📋 Metas Programadas: {datos_pbr.get('total_metas_programadas', 0)}", className="mb-0 text-muted", style={"fontSize": "0.75rem"})
                ], md=6),
                dbc.Col([
                    html.P(f"✅ Metas Alcanzadas: {datos_pbr.get('total_metas_alcanzadas', 0)}", className="mb-1 font-weight-bold", style={"fontSize": "0.85rem"}),
                    html.P(f"💬 Estatus: {datos_pbr.get('mensaje', '')}", className="mb-0 text-muted", style={"fontSize": "0.75rem"})
                ], md=6)
            ])
        ], color=color_alerta, className="shadow-sm border-0 mb-4")
    return dbc.Alert("Formato de indicadores no reconocido.", color="warning")


# --- CALLBACKS DE NAVEGACIÓN: ACUERDOS INSTITUCIONALES ---
@app.callback(
    Output('contenedor-tarjetas-acuerdos', 'children'),
    Input('contenedor-tarjetas-acuerdos', 'id')
)
def cargar_acuerdos(_):
    import plotly.graph_objects as go
    conn = sqlite3.connect(DB_GESTION)
    df = pd.read_sql_query("SELECT * FROM acuerdos", conn)
    conn.close()
    
    tarjetas = []
    for _, f in df.iterrows():
        id_acuerdo = f['id']
        nombre_acuerdo = f['nombre']
        porcentaje_base = 85 if id_acuerdo == 1 else (70 if id_acuerdo == 2 else (90 if id_acuerdo == 3 else 60))
        icono_clase = DICCIONARIO_ICONOS_ACUERDOS.get(id_acuerdo, "bi bi-folder")
        
        fig_dona = go.Figure(go.Pie(values=[porcentaje_base, 100 - porcentaje_base], hole=0.72, marker_colors=["#691c32", "#e5e7eb"], textinfo='none', hoverinfo='none'))
        fig_dona.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), width=75, height=75, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        tarjetas.append(dbc.Col(html.Div([
            html.Div([
                html.I(className=icono_clase, style={"position": "absolute", "fontSize": "1.3rem", "color": "#691c32", "zIndex": "10"}),
                dcc.Graph(figure=fig_dona, config={'displayModeBar': False})
            ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "position": "relative", "marginBottom": "15px"}),
            html.P(nombre_acuerdo, className="text-center mb-2 font-weight-bold", style={"fontSize": "0.78rem", "color": "#1f2937", "lineHeight": "1.4"}),
            html.H6(f"{porcentaje_base}%", className="text-center font-weight-bold", style={"color": "#691c32", "fontSize": "0.9rem", "margin": "0"}),
            dbc.Button("", id={'type': 'btn-acuerdo', 'index': id_acuerdo}, style={"position": "absolute", "top": "0", "left": "0", "width": "100%", "height": "100%", "opacity": "0", "cursor": "pointer", "zIndex": "20"})
        ], className="p-4 bg-white border text-center position-relative h-100 shadow-sm", style={"borderRadius": "18px", "borderColor": "#e5e7eb"}), width=12, sm=6, md=3, className="mb-4"))
    return tarjetas

@app.callback(
    [Output('collapse-areas', 'is_open'), Output('contenedor-botones-areas', 'children')],
    [Input({'type': 'btn-acuerdo', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def desplegar_areas(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None): return False, ""
    idx = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    conn = sqlite3.connect(DB_GESTION)
    df = pd.read_sql_query(f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn)
    conn.close()
    botones = [dbc.Button(a['nombre'], id={'type': 'btn-area', 'index': a['id']}, color="outline-primary", className="m-2") for _, a in df.iterrows()]
    return True, botones


# --- DASHBOARD DE ÁREA OPERATIVA MUNICIPAL ---
@app.callback(
    [Output('contenido-area', 'children'), Output('active-info', 'data'), Output('resumen-kpis', 'children')],
    [Input({'type': 'btn-area', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def mostrar_dashboard(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None): return "", no_update, ""
    idx = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    conn = sqlite3.connect(DB_GESTION)
    area_data = pd.read_sql_query("SELECT nombre FROM areas WHERE id=?", conn, params=(idx,))
    
    if area_data.empty: 
        conn.close()
        return dbc.Alert("Área no registrada."), no_update, ""
        
    nombre_area = area_data.iloc[0]['nombre']
    tabla = normalizar_nombre_tabla(nombre_area)
    
    info_est = DICCIONARIO_AREAS.get(tabla, {
        "resumen": "Área operativa integrada en los acuerdos del Plan Municipal.",
        "objetivo": "Seguimiento y evaluación continua de los indicadores sectoriales."
    })
    
    try:
        df = pd.read_sql_query(f'SELECT rowid, * FROM "{tabla}"', conn)
        conn.close()
        
        datos_pbr_raw = calcular_indicadores_pbr(df)
        resumen_cards = diseñar_tarjeta_pbr(datos_pbr_raw)

        bloque_resumen = dbc.Alert([
            html.H5(f"📌 RESUMEN ESTRATÉGICO: {nombre_area}", className="alert-heading font-weight-bold", style={"fontSize": "0.95rem"}),
            html.P(info_est['resumen'], className="mb-2", style={"fontSize": "0.82rem"}),
            html.Hr(style={"margin": "8px 0"}),
            html.Small(f"🎯 OBJETIVO GENERAL: {info_est['objetivo']}", className="text-muted font-italic", style={"fontSize": "0.78rem"})
        ], color="light", className="mt-2 mb-4 border-start border-primary", style={'borderLeftWidth': '5px'})

        contenido = html.Div([
            dbc.Row([
                dbc.Col(html.H2(f"📊 {nombre_area}", className="text-primary font-weight-bold", style={"fontSize": "1.5rem"}), md=9),
                dbc.Col(html.Div(id='notif-area'), md=3)
            ], className="mb-3 align-items-center"),
            
            bloque_resumen,
            
            dash_table.DataTable(
                id='main-table', data=df.to_dict('records'),
                columns=[{"name": i.upper(), "id": i, "editable": (i != 'rowid')} for i in df.columns],
                row_deletable=True, page_size=5, editable=True, filter_action="native",
                style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontWeight': 'bold'},
                style_table={'overflowX': 'auto', 'marginBottom': '30px'}
            ),
            seccion_impacto_layout()
        ])
        return contenido, {'tabla': tabla, 'id': idx}, resumen_cards
    except Exception as e:
        if 'conn' in locals(): conn.close()
        return dbc.Alert(f"Error al cargar la tabla unificada: {e}", color="danger"), no_update, ""


# --- INTEGRACIÓN DE AUTO-SAVE (SEGUNDO PLANO) ---
@app.callback(
    Output("notif-area", "children"),
    [Input("main-table", "data"), Input("main-table", "data_previous")],
    State("active-info", "data"),
    prevent_initial_call=True
)
def cb_guardar_automatico(rows, rows_previos, info):
    if rows is None or info is None: return no_update
    if rows_previos is not None and rows == rows_previos: return no_update
    try:
        df = pd.DataFrame(rows)
        if 'rowid' in df.columns: df = df.drop(columns=['rowid'])
        conn = sqlite3.connect(DB_GESTION)
        df.to_sql(info['tabla'], conn, if_exists='replace', index=False)
        conn.close()
        return dbc.Badge("✏️ Cambios guardados automáticamente", color="success", className="p-2 w-100 text-white shadow-sm")
    except Exception as e:
        return dbc.Badge(f"⚠️ Error al guardar: {e}", color="danger", className="p-2 w-100 text-white")


# --- ACTUALIZACIÓN DE GRÁFICAS DE IMPACTO ---
@app.callback(
    Output('contenedor-graficas-impacto', 'children'),
    Input('main-table', 'data'),
    State('active-info', 'data')
)
def actualizar_graficas(rows, info):
    if not rows or not info: 
        return no_update
    return generar_tablero_impacto(pd.DataFrame(rows), nombre_tabla=info['tabla'])


# --- GESTIÓN DE MODALES ---
@app.callback(
    [Output("modal-config", "is_open"), Output("modal-update", "is_open"), Output("modal-borrado-admin", "is_open"),
     Output("update-area-selector", "options"), Output("borrar-area-selector", "options")],
    [Input("btn-abrir-config", "n_clicks"), Input("btn-abrir-update", "n_clicks"), Input("btn-abrir-borrado-seccion", "n_clicks"), Input("btn-cerrar-borrado", "n_clicks")],
    [State("modal-config", "is_open"), State("modal-update", "is_open"), State("modal-borrado-admin", "is_open")],
    prevent_initial_call=True
)
def gestion_modales(n1, n2, n3, n4, s1, s2, s3):
    ctx = dash.callback_context
    bid = ctx.triggered[0]['prop_id'].split('.')[0]
    opts = []
    if bid in ["btn-abrir-update", "btn-abrir-borrado-seccion"]:
        conn = sqlite3.connect(DB_GESTION)
        df = pd.read_sql_query("SELECT id, nombre FROM areas", conn); conn.close()
        opts = [{'label': r['nombre'], 'value': r['id']} for _, r in df.iterrows()]
    if bid == "btn-abrir-config": return True, False, False, [], []
    if bid == "btn-abrir-update": return False, True, False, opts, []
    if bid == "btn-abrir-borrado-seccion": return False, False, True, [], opts
    return False, False, False, [], []


# --- CREACIÓN Y CONFIGURACIÓN DE NUEVAS ÁREAS (CON LIMPIEZA STRIP) ---
@app.callback(
    Output("salida-confirmacion", "children"),
    Input("btn-guardar-excel", "n_clicks"),
    [State("input-nombre-area", "value"), State("input-acuerdo-id", "value"), State("area-texto-excel", "value")],
    prevent_initial_call=True
)
def cb_nueva_area(n, nom, ac, txt):
    if not nom or not txt or ac is None: 
        return dbc.Alert("⚠️ Faltan datos obligatorios. Ingrese el nombre, el acuerdo y los datos.", color="warning")
    try:
        tab = normalizar_nombre_tabla(nom)
        
        if "docs.google.com" in txt:
            url_final = obtener_url_csv(txt)
            df = pd.read_csv(url_final)
        else:
            df = pd.read_csv(StringIO(txt), sep='\t')
            
        # Limpieza estricta de nombres de columnas removiendo espacios fantasmas
        df.columns = [str(c).strip() for c in df.columns]
        
        conn = sqlite3.connect(DB_GESTION)
        df.to_sql(tab, conn, if_exists='replace', index=False)
        
        nombre_area_limpio = str(nom).upper().strip()
        conn.execute("INSERT INTO areas (nombre, acuerdo_id) VALUES (?, ?)", (nombre_area_limpio, ac))
        conn.commit()
        conn.close()
        
        return dbc.Alert(f"✅ Área '{nombre_area_limpio}' y tabla '{tab}' creadas exitosamente.", color="success")
    except Exception as e: 
        if 'conn' in locals(): conn.close()
        return dbc.Alert(f"⚠️ Error al crear el área: {e}", color="danger")


# --- SINCRONIZACIÓN DE DATOS / APPEND ---
@app.callback(
    Output("update-status", "children"),
    Input("btn-update-validar", "n_clicks"),
    [State("update-area-selector", "value"), State("update-texto-excel", "value")],
    prevent_initial_call=True
)
def cb_agregar_datos(n, aid, txt):
    if not aid or not txt: 
        return dbc.Alert("⚠️ Seleccione un área e introduzca los nuevos datos.", color="warning")
    try:
        conn = sqlite3.connect(DB_GESTION)
        area_info = pd.read_sql_query("SELECT nombre FROM areas WHERE id=?", conn, params=(aid,)).iloc[0]
        tabla = normalizar_nombre_tabla(area_info['nombre'])
        
        if "docs.google.com" in txt:
            df_nuevos = pd.read_csv(obtener_url_csv(txt))
        else:
            df_nuevos = pd.read_csv(StringIO(txt), sep='\t')
            
        df_nuevos.columns = [str(c).strip() for c in df_nuevos.columns]
        df_nuevos.to_sql(tabla, conn, if_exists='append', index=False)
        conn.close()
        return dbc.Alert(f"✅ Datos agregados correctamente a la sección {area_info['nombre']}", color="success")
    except Exception as e: 
        if 'conn' in locals(): conn.close()
        return dbc.Alert(f"⚠️ Error al sincronizar: {e}", color="danger")


# --- ELIMINAR SECCIONES ---
@app.callback(
    Output("borrar-status", "children"),
    Input("btn-confirmar-borrado-final", "n_clicks"),
    State("borrar-area-selector", "value"),
    prevent_initial_call=True
)
def cb_borrar_area(n, aid):
    if not aid: 
        return dbc.Alert("⚠️ Seleccione un área para eliminar.", color="warning")
    try:
        conn = sqlite3.connect(DB_GESTION)
        area_info = pd.read_sql_query("SELECT nombre FROM areas WHERE id=?", conn, params=(aid,)).iloc[0]
        tabla = normalizar_nombre_tabla(area_info['nombre'])
        
        conn.execute(f'DROP TABLE IF EXISTS "{tabla}"')
        conn.execute("DELETE FROM areas WHERE id=?", (aid,))
        conn.commit()
        conn.close()
        return dbc.Alert(f"🗑️ El área '{area_info['nombre']}' ha sido eliminada del sistema.", color="success")
    except Exception as e: 
        if 'conn' in locals(): conn.close()
        return dbc.Alert(f"⚠️ Error al eliminar: {e}", color="danger")

if __name__ == "__main__":
    app.run(debug=True, port=8050)
