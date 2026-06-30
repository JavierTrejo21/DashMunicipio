# indicadores_pbr.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dash_table
import os

def calcular_indicadores_pbr(df_tabla_activa, nombre_tabla_activa=""):
    """
    Cédula Automática PbR - DES01.
    Versión Diagnóstica Definitiva para romper el bucle de errores.
    """
    # 1. LOCALIZAR EL ARCHIVO EN LA RAÍZ
    ruta_des01 = None
    archivos_en_raiz = os.listdir('.')
    
    for archivo in archivos_en_raiz:
        if "DES01" in archivo.upper() and (archivo.lower().endswith(".xlsx") or archivo.lower().endswith(".csv")):
            ruta_des01 = archivo
            break
            
    if not ruta_des01:
        return dbc.Alert("⚠️ No se encontró el archivo DES01 en la raíz de C:\\DashMunicipio.", color="danger")

    # 2. LEER DESDE LA FILA EXACTA DE ENCABEZADOS
    try:
        if ruta_des01.lower().endswith(".csv"):
            # Buscar dónde está la cabecera real en el CSV
            fila_encabezado = 0
            df_test = pd.read_csv(ruta_des01, nrows=6, header=None)
            for i, fila in df_test.iterrows():
                valores = [str(val).upper() for val in fila.values]
                if any("UNIDAD" in val or "RESPONSABLE" in val for val in valores):
                    fila_encabezado = i
                    break
            df_des01 = pd.read_csv(ruta_des01, header=fila_encabezado)
        else:
            df_raw = pd.read_excel(ruta_des01, header=None)
            fila_encabezado = 0  
            for i, fila in df_raw.head(6).iterrows():
                valores_fila = [str(val).upper() for val in fila.values]
                if any("UNIDAD" in val or "RESPONSABLE" in val for val in valores_fila):
                    fila_encabezado = i
                    break
            df_des01 = pd.read_excel(ruta_des01, header=fila_encabezado)
            
    except Exception as e:
        return dbc.Alert(f"⚠️ Error al leer el archivo: {str(e)}", color="danger")

    # Limpiar nombres de columnas
    df_des01.columns = [str(c).strip().upper() for c in df_des01.columns]

    # Ubicar la columna Unidad Responsable
    col_ur = next((c for c in df_des01.columns if "UNIDAD" in c or "RESPONSABLE" in c), None)
    col_nivel = next((c for c in df_des01.columns if "NIVEL" in c), None)
    col_resumen = next((c for c in df_des01.columns if "RESUMEN" in c or "NARRATIVO" in c), None)
    col_indicador = next((c for c in df_des01.columns if "NOMBRE DEL INDICADOR" in c or "INDICADOR" in c), None)
    col_meta = next((c for c in df_des01.columns if "META" in c or "ANUAL" in c), None)

    if not col_ur:
        return dbc.Alert("⚠️ No se localizó la columna de Unidad Responsable en el archivo.", color="danger")

    # 3. EL FILTRADO DIRECTO
    # Convertimos a strings limpios sin espacios extras a los lados
    area_solicitada = str(nombre_tabla_activa).strip()
    df_des01[col_ur] = df_des01[col_ur].astype(str).str.strip()

    # Intentar match directo
    df_area_mir = df_des01[df_des01[col_ur] == area_solicitada].copy()

    # Si falla, intentar ignorando mayúsculas/minúsculas
    if df_area_mir.empty:
        df_area_mir = df_des01[df_des01[col_ur].str.upper() == area_solicitada.upper()].copy()

    # Si sigue fallando, intentar buscando coincidencias parciales (ej: si busca "DIF" y en excel dice "DIF Municipal")
    if df_area_mir.empty:
        palabra_clave = area_solicitada.replace('_', ' ').split(' ')[0]
        if len(palabra_clave) > 2: # Evitar filtrar por cosas cortas vacías
            df_area_mir = df_des01[df_des01[col_ur].str.contains(palabra_clave, na=False, case=False)].copy()

    # 4. PANEL DE CONTROL DE ERRORES (Si no encuentra el área, te dice el por qué exacto)
    if df_area_mir.empty:
        unidades_en_excel = df_des01[col_ur].dropna().unique()
        return html.Div([
            dbc.Alert("🔍 PANEL DE DIAGNÓSTICO: ERROR DE COINCIDENCIA", color="warning", className="fw-bold"),
            html.P([
                "Para la pestaña actual, la variable de tu base de datos/Dash está enviando al código el texto: ", 
                html.B(f"'{nombre_tabla_activa}'", style={"color": "#b91c1c", "fontSize": "1.1rem"})
            ]),
            html.P("Sin poner excusas, tu archivo Excel contiene únicamente las siguientes áreas:"),
            html.Div([
                html.Ul([html.Li(html.Code(u, style={"fontSize": "1rem"})) for u in unidades_en_excel if "EJE" not in u.upper()])
            ], className="p-3 bg-white border rounded mb-3"),
            html.Div([
                html.Span("💡 Solución rápida: ", className="fw-bold text-success"),
                "Abre tu archivo Excel, ve a la columna ", html.B(f"'{col_ur}'"), " y reescribe el nombre de tu área para que sea idéntico a la alerta roja que ves arriba."
            ], className="p-2 bg-success bg-opacity-10 border border-success rounded text-dark small")
        ], className="p-4 border rounded bg-light shadow-sm mb-4")

    # 5. GENERAR TABLA SI EL FILTRO FUE EXITOSO
    df_cedula = pd.DataFrame()
    df_cedula['Nivel'] = df_area_mir[col_nivel].fillna("ACTIVIDAD").astype(str).str.upper()
    df_cedula['Indicador'] = df_area_mir[col_resumen].fillna("").astype(str) + " — " + df_area_mir[col_indicador].fillna("").astype(str)
    
    # Manejo seguro de la meta
    if col_meta:
        df_cedula['Meta Anual'] = pd.to_numeric(df_area_mir[col_meta], errors='coerce').fillna(0)
    else:
        df_cedula['Meta Anual'] = 0

    # Buscar columnas de semáforos
    semaforos = [c for c in df_des01.columns if "SEMÁFORO" in c or "SEMAFORO" in c]
    df_cedula['Semaforo T1'] = df_area_mir[semaforos[0]].fillna("VERDE").astype(str).str.upper().str.strip() if len(semaforos) >= 1 else "VERDE"
    df_cedula['Semaforo Anual'] = df_area_mir[semaforos[-1]].fillna("VERDE").astype(str).str.upper().str.strip() if len(semaforos) >= 2 else "VERDE"

    # Limpiar filas vacías
    df_cedula = df_cedula[df_cedula['Indicador'].str.strip() != "—"]
    datos_tabla = df_cedula.to_dict('records')

    return html.Div([
        html.Div([
            html.I(className="bi bi-shield-check me-2", style={"color": "#691c32"}),
            html.Span(f"CÉDULA PbR: MATRIZ DE INDICADORES", style={"fontWeight": "bold", "color": "#1f2937"}),
            dbc.Badge(area_solicitada.upper(), color="success", className="float-end")
        ], className="p-2 border-bottom mb-3 bg-light", style={"borderLeft": "4px solid #691c32"}),

        dash_table.DataTable(
            data=datos_tabla,
            columns=[
                {"name": "Nivel MIR", "id": "Nivel"},
                {"name": "Objetivo / Resumen Narrativo del Indicador", "id": "Indicador"},
                {"name": "Meta Anual", "id": "Meta Anual"},
                {"name": "Estatus T1", "id": "Semaforo T1"},
                {"name": "Estatus Anual", "id": "Semaforo Anual"}
            ],
            style_header={'backgroundColor': '#691c32', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'center'},
            style_data={'fontSize': '11px', 'whiteSpace': 'normal', 'height': 'auto'},
            style_cell={'padding': '8px', 'textAlign': 'left'},
            style_cell_conditional=[
                {'if': {'column_id': 'Nivel'}, 'width': '12%', 'textAlign': 'center', 'fontWeight': 'bold'},
                {'if': {'column_id': 'Indicador'}, 'width': '53%'},
                {'if': {'column_id': 'Meta Anual'}, 'width': '11%', 'textAlign': 'center'},
                {'if': {'column_id': 'Semaforo T1'}, 'width': '12%', 'textAlign': 'center'},
                {'if': {'column_id': 'Semaforo Anual'}, 'width': '12%', 'textAlign': 'center'},
            ],
            style_data_conditional=[
                {'if': {'column_id': 'Semaforo T1', 'filter_query': '{Semaforo T1} contains "VERDE"'}, 'backgroundColor': '#dcfce7', 'color': '#15803d', 'fontWeight': 'bold'},
                {'if': {'column_id': 'Semaforo T1', 'filter_query': '{Semaforo T1} contains "AMARILLO"'}, 'backgroundColor': '#fef9c3', 'color': '#a16207', 'fontWeight': 'bold'},
                {'if': {'column_id': 'Semaforo T1', 'filter_query': '{Semaforo T1} contains "ROJO"'}, 'backgroundColor': '#fee2e2', 'color': '#b91c1c', 'fontWeight': 'bold'},
                {'if': {'column_id': 'Semaforo Anual', 'filter_query': '{Semaforo Anual} contains "VERDE"'}, 'backgroundColor': '#dcfce7', 'color': '#15803d', 'fontWeight': 'bold'},
                {'if': {'column_id': 'Semaforo Anual', 'filter_query': '{Semaforo Anual} contains "AMARILLO"'}, 'backgroundColor': '#fef9c3', 'color': '#a16207', 'fontWeight': 'bold'},
                {'if': {'column_id': 'Semaforo Anual', 'filter_query': '{Semaforo Anual} contains "ROJO"'}, 'backgroundColor': '#fee2e2', 'color': '#b91c1c', 'fontWeight': 'bold'},
            ],
            page_size=6
        )
    ], className="mb-4 bg-white p-3 border rounded shadow-sm")
