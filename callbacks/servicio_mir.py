import os
import re
import pandas as pd
from dash import html

# Importación relativa dentro de la carpeta callbacks
from .componentes_navegacion import diseñar_tabla_mir_consolidada


def generar_resumen_indicadores_area(nombre_area):
    """Lee el Excel DES01_CHU_02_2026.xlsx y extrae las columnas requeridas de forma flexible"""
    ruta_excel = "DES01_CHU_02_2026.xlsx"

    if not os.path.exists(ruta_excel):
        return html.Div()

    try:
        df_raw = pd.read_excel(ruta_excel, header=None)
        fila_encabezado = 0
        for i, fila in df_raw.head(10).iterrows():
            valores_fila = [str(val).upper() for val in fila.values]
            if any("UNIDAD" in val or "RESPONSABLE" in val or "PROGRAMA" in val for val in valores_fila):
                fila_encabezado = i
                break

        df_excel = pd.read_excel(ruta_excel, header=fila_encabezado)

        indices_cols = [6, 8, 9, 12, 14, 24, 28, 32, 36, 38, 39, 40]
        indices_validos = [idx for idx in indices_cols if idx < len(df_excel.columns)]

        if not indices_validos:
            return html.Div()

        # Buscar en qué columna se encuentra la unidad responsable o texto descriptivo (revisando las primeras 5 columnas)
        col_ur_idx = 2
        for c_idx in range(min(5, len(df_excel.columns))):
            muestra_col = df_excel.iloc[:, c_idx].astype(str).str.cat(sep=" ").upper()
            if "DIRECCION" in muestra_col or "UNIDAD" in muestra_col or "COORDINACION" in muestra_col or "DIF" in muestra_col:
                col_ur_idx = c_idx
                break

        # Limpiar texto de la columna seleccionada
        df_excel.iloc[:, col_ur_idx] = (
            df_excel.iloc[:, col_ur_idx]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.upper()
        )

        area_busqueda = str(nombre_area).replace(r"\s+", " ").strip().upper()
        
        # Estrategia 1: Coincidencia exacta o parcial del nombre completo
        df_filtrado = df_excel[df_excel.iloc[:, col_ur_idx].str.contains(re.escape(area_busqueda), na=False)]

        # Estrategia 2: Si no encuentra, buscar por la clave numérica o código inicial (ej. "2.2.5" o "1.7")
        if df_filtrado.empty:
            clave_match = re.search(r"([\d\.]+)", area_busqueda)
            if clave_match:
                clave = clave_match.group(1)
                df_filtrado = df_excel[df_excel.iloc[:, col_ur_idx].str.contains(re.escape(clave), na=False)]

        # Estrategia 3: Si aun así está vacío, buscar por palabras clave significativas (ignorando palabras de enlace)
        if df_filtrado.empty:
            palabras = [p for p in area_busqueda.split() if len(p) > 3 and p not in {'DEL', 'LA', 'DE', 'EL', 'LOS', 'LAS', 'Y'}]
            if palabras:
                patron = "|".join(re.escape(p) for p in palabras)
                df_filtrado = df_excel[df_excel.iloc[:, col_ur_idx].str.contains(patron, na=False)]

        if df_filtrado.empty:
            return html.Div([
                html.Small(f"ℹ️ Sin datos MIR vinculados para: {nombre_area}", className="text-muted p-2 d-block")
            ])

        df_resultado = df_filtrado.iloc[:, indices_validos].copy()
        df_resultado.dropna(how="all", inplace=True)

        if df_resultado.empty:
            return html.Div()

        return diseñar_tabla_mir_consolidada(df_resultado)

    except Exception as e:
        print(f"Error procesando servicio_mir para {nombre_area}: {e}")
        return html.Div()