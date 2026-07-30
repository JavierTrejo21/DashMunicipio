import os
import re
import pandas as pd
from dash import html

# Importación relativa dentro de la carpeta callbacks
from .componentes_navegacion import diseñar_tabla_mir_consolidada


def generar_resumen_indicadores_area(nombre_area):
    """Lee el Excel DES01_CHU_02_2026.xlsx y extrae las columnas requeridas"""
    ruta_excel = "DES01_CHU_02_2026.xlsx"

    if not os.path.exists(ruta_excel):
        return html.Div()

    try:
        df_raw = pd.read_excel(ruta_excel, header=None)
        fila_encabezado = 0
        for i, fila in df_raw.head(6).iterrows():
            valores_fila = [str(val).upper() for val in fila.values]
            if any(
                "UNIDAD" in val or "RESPONSABLE" in val for val in valores_fila
            ):
                fila_encabezado = i
                break

        df_excel = pd.read_excel(ruta_excel, header=fila_encabezado)

        indices_cols = [6, 8, 9, 12, 14, 24, 28, 32, 36, 38, 39, 40]
        indices_validos = [
            idx for idx in indices_cols if idx < len(df_excel.columns)
        ]

        if not indices_validos:
            return html.Div()

        col_ur_idx = 2
        df_excel.iloc[:, col_ur_idx] = (
            df_excel.iloc[:, col_ur_idx]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        area_busqueda = (
            str(nombre_area).replace(r"\s+", " ").strip().upper()
        )
        df_filtrado = df_excel[
            df_excel.iloc[:, col_ur_idx]
            .astype(str)
            .str.upper()
            .str.contains(area_busqueda, na=False)
        ]

        if df_filtrado.empty:
            clave_match = re.match(r"^([\d\.]+)", area_busqueda)
            if clave_match:
                clave = clave_match.group(1)
                df_filtrado = df_excel[
                    df_excel.iloc[:, col_ur_idx]
                    .astype(str)
                    .str.contains(clave, na=False)
                ]

        if df_filtrado.empty:
            return html.Div()

        df_resultado = df_filtrado.iloc[:, indices_validos].copy()
        df_resultado.dropna(how="all", inplace=True)

        if df_resultado.empty:
            return html.Div()

        return diseñar_tabla_mir_consolidada(df_resultado)

    except Exception:
        return html.Div()
