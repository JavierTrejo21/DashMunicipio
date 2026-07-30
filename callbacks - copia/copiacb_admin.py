import sqlite3
import pandas as pd
from io import StringIO
from dash import Input, Output, State
import dash
import dash_bootstrap_components as dbc

from database import normalizar_nombre_tabla, DB_GESTION

def obtener_url_csv(url_sheets):
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

def register_admin_callbacks(app):

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
