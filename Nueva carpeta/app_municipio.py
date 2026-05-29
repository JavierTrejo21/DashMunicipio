import dash
from dash import dcc, html, Input, Output, ALL, dash_table
import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import json

# === 1. CONFIGURACIÓN DE BASES DE DATOS ===
DB_GESTION = 'gestion_municipal.db'
DB_OBRAS = 'municipio.db'

def cargar_datos_obras():
    try:
        conn = sqlite3.connect(DB_OBRAS)
        # Verificamos qué tablas existen realmente en tu municipio.db
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [t[0] for t in cursor.fetchall()]
        
        # Intentamos leer 'proyectos', si no existe, intentamos con la primera que encuentre
        tabla_a_leer = 'proyectos' if 'proyectos' in tablas else tablas[0]
        
        df = pd.read_sql_query(f"SELECT * FROM {tabla_a_leer}", conn)
        conn.close()
        
        if df.empty: return pd.DataFrame()

        # MAPEADOR UNIVERSAL (Busca fragmentos para no fallar por nombres largos)
        mapeo = {}
        for col in df.columns:
            c = col.lower()
            if 'ubicacion' in c: mapeo[col] = 'ubicacion'
            elif 'monto' in c: mapeo[col] = 'monto_total'
            elif 'estatus' in c: mapeo[col] = 'estatus_obra'
            elif 'beneficiarios' in c: mapeo[col] = 'beneficiarios'
            elif 'avance' in c: mapeo[col] = 'avance'
            elif 'nombre' in c and 'proy' in c: mapeo[col] = 'nombre_proyecto'
        
        df = df.rename(columns=mapeo)

        # Limpieza de datos
        for col in ['monto_total', 'beneficiarios', 'avance']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.replace('%', '', regex=False).str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        print(f"Error crítico: {e}")
        return pd.DataFrame()

# === 2. APLICACIÓN DASH ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP])

# (El resto del layout se mantiene igual al que te envié anteriormente)
# ... [Mantén aquí el layout de tarjetas y botones que ya tenías] ...

@app.callback(
    Output('detalle-contenido', 'children'),
    Input({'type': 'btn-area', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def renderizar_detalle(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks): return ""
    
    area_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    
    # Consultamos el código del área
    conn = sqlite3.connect(DB_GESTION)
    area_info = pd.read_sql_query(f"SELECT * FROM areas WHERE id = {area_id}", conn)
    conn.close()
    
    codigo = area_info.iloc[0]['codigo_informe']
    nombre = area_info.iloc[0]['nombre']

    # Si es Obras Públicas (4.5)
    if codigo == '4.5':
        df = cargar_datos_obras()
        if df.empty:
            return dbc.Alert(f"Atención: La tabla en municipio.db está vacía o no tiene el formato correcto.", color="warning")
        
        # Aquí generamos el Dashboard que antes estaba en dashboard.py
        # [Tarjetas de KPI, Gráficas y Tabla]
        # (Usa el bloque de retorno que te pasé en el código completo anterior)
        return generar_panel_obras(df, nombre) # Función auxiliar para limpiar el código

    return dbc.Alert(f"El módulo para {nombre} está bajo construcción.", color="info")

def generar_panel_obras(df, nombre):
    # Lógica de gráficas de dashboard.py integrada aquí
    presupuesto = df['monto_total'].sum()
    fig_estatus = px.bar(df.groupby('estatus_obra')['monto_total'].sum().reset_index(), 
                         x="estatus_obra", y="monto_total", title="Inversión por Estatus", template="plotly_white")
    
    return html.Div([
        html.H3(f"PANEL: {nombre}"),
        html.H4(f"Inversión Total: ${presupuesto:,.2f}", className="text-success"),
        dcc.Graph(figure=fig_estatus),
        dash_table.DataTable(data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'})
    ])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
