# pbr_modules/pbr_generico.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dash_table
import os

def calcular_pbr_generico(df):
    """
    Motor Central Único PbR - Creado desde Cero.
    - Obtiene dinámicamente el nombre de la Unidad Responsable activa.
    - Carga directamente el Excel maestro de la raíz.
    - Limpia saltos de línea de la columna C y enlaza con la interfaz.
    """
    ruta_excel = "DES01_CHU_02_2026.xlsx"
    
    # 1. DETECTAR EL ÁREA ACTIVA DESDE LA INTERFAZ
    col_ur_candidatos = [c for c in df.columns if "UNIDAD" in str(c).upper() or "RESPONSABLE" in str(c).upper()]
    
    if col_ur_candidatos and len(df) > 0:
        area_detectada = str(df[col_ur_candidatos[0]].iloc[0]).strip()
    else:
        return dbc.Alert("🔍 Seleccione una Unidad Responsable en el menú para visualizar sus indicadores MIR.", color="info", className="fw-bold m-2")

    # 2. SEGURO DE EXISTENCIA DEL ARCHIVO
    if not os.path.exists(ruta_excel):
        return dbc.Alert(f"⚠️ Archivo maestro '{ruta_excel}' no detectado en la raíz del sistema.", color="danger", className="m-2")

    # 3. LEER EXCEL LOCALIZANDO LOS ENCABEZADOS DE FORMA INTELIGENTE
    try:
        df_raw = pd.read_excel(ruta_excel, header=None)
        fila_encabezado = 0  
        for i, fila in df_raw.head(6).iterrows():
            valores_fila = [str(val).upper() for val in fila.values]
            if any("UNIDAD" in val or "RESPONSABLE" in val for val in valores_fila):
                fila_encabezado = i
                break
        df_des01 = pd.read_excel(ruta_excel, header=fila_encabezado)
    except Exception as e:
        return dbc.Alert(f"❌ Error crítico al abrir el Excel maestro: {str(e)}", color="danger", className="m-2")

    # Normalizar los nombres de las columnas a mayúsculas
    df_des01.columns = [str(c).strip().upper() for c in df_des01.columns]
    
    col_ur = next((c for c in df_des01.columns if "UNIDAD" in c or "RESPONSABLE" in c), None)
    col_nivel = next((c for c in df_des01.columns if "NIVEL" in c), None)
    col_resumen = next((c for c in df_des01.columns if "RESUMEN" in c or "NARRATIVO" in c), None)
    col_indicador = next((c for c in df_des01.columns if "NOMBRE DEL INDICADOR" in c or "INDICADOR" in c), None)
    col_meta = next((c for c in df_des01.columns if "META" in c or "ANUAL" in c), None)

    if not col_ur:
        return dbc.Alert("⚠️ No se localizó la columna de Unidad Responsable (Columna C) en el documento Excel.", color="danger", className="m-2")

    # 4. LIMPIEZA CLAVE DE SALTOS DE LÍNEA E INCONSISTENCIAS DE TEXTO
    df_des01[col_ur] = df_des01[col_ur].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    texto_busqueda = area_detectada.replace(r'\s+', ' ').strip()

    # Intento 1: Coincidencia Exacta
    df_area_mir = df_des01[df_des01[col_ur].str.upper() == texto_busqueda.upper()].copy()

    # Intento 2: Coincidencia Parcial (Rescate por palabra clave si falla algún punto o número)
    if df_area_mir.empty:
        palabra_clave = texto_busqueda.split(' ')[-1] # Ej. toma "SOCIAL" o "MUJERES"
        if len(palabra_clave) > 3:
            df_area_mir = df_des01[df_des01[col_ur].str.contains(palabra_clave, na=False, case=False)].copy()

    # Si no tiene registros asignados en la matriz
    if df_area_mir.empty:
        return dbc.Alert(f"📋 El área '{area_detectada}' no cuenta con registros de indicadores MIR válidos en este ejercicio.", color="warning", className="m-2")

    # 5. ESTRUCTURAR EL CONTENIDO DE LA CÉDULA
    df_cedula = pd.DataFrame()
    df_cedula['Nivel'] = df_area_mir[col_nivel].fillna("ACTIVIDAD").astype(str).str.upper()
    df_cedula['Indicador'] = df_area_mir[col_resumen].fillna("").astype(str) + " — " + df_area_mir[col_indicador].fillna("").astype(str)
    df_cedula['Meta Anual'] = pd.to_numeric(df_area_mir[col_meta], errors='coerce').fillna(0) if col_meta else 0

    # Capturar columnas de semáforos
    semaforos = [c for c in df_des01.columns if "SEMÁFORO" in c or "SEMAFORO" in c]
    df_cedula['Semaforo T1'] = df_area_mir[semaforos[0]].fillna("VERDE").astype(str).str.upper().str.strip() if len(semaforos) >= 1 else "VERDE"
    df_cedula['Semaforo Anual'] = df_area_mir[semaforos[-1]].fillna("VERDE").astype(str).str.upper().str.strip() if len(semaforos) >= 2 else "VERDE"

    df_cedula = df_cedula[df_cedula['Indicador'].str.strip() != "—"]
    datos_tabla = df_cedula.to_dict('records')

    # 6. RETORNAR EL COMPONENTE VISUAL CON FORMATO DE TABLA
    return html.Div([
        html.Div([
            html.I(className="bi bi-grid-3x3-gap-fill me-2", style={"color": "#691c32"}),
            html.Span("MATRIZ DE INDICADORES (MIR) AUTOMÁTICA", style={"fontWeight": "bold", "color": "#1f2937", "fontSize": "12px"}),
            dbc.Badge(area_detectada.upper(), color="success", className="float-end", style={"fontSize": "11px"})
        ], className="p-2 border-bottom mb-3 bg-light", style={"borderLeft": "4px solid #691c32"}),

        dash_table.DataTable(
            data=datos_tabla,
            columns=[
                {"name": "Nivel MIR", "id": "Nivel"},
                {"name": "Objetivo / Nombre del Indicador", "id": "Indicador"},
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
            page_size=10
        )
    ], className="mb-4 bg-white p-3 border rounded shadow-sm")
