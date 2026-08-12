# areas/mir_general.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html
import os

# ==========================================
# PALETA INSTITUCIONAL (misma que el resto del sistema)
# ==========================================
PALETTE = {
    "guinda":        "#7A1E3D",
    "guinda_dark":    "#5A1530",
    "guinda_deep":    "#3A0F20",   # para el bloque de mayor jerarquía (AVANCE / RESULTADO)
    "guinda_light":   "#F6E9EE",
    "verde":          "#136F63",
    "verde_dark":     "#0C5148",
    "verde_light":    "#E5F3F0",
    "gold":           "#B5892C",
    "gold_dark":      "#8A6512",
    "gold_light":     "#F6EFDD",
    "ink":            "#241E1B",   # header de subcolumnas y texto de celda
    "ink_soft":       "#6B625C",
    "ink_faint":      "#9B928C",
    "line":           "#E3DDD2",   # bordes de celda
    "stripe":         "#FBFAF7",   # fila par
    "card_head_bg":   "#F6F3EE",   # franja superior del título de la tarjeta
}


# ==========================================
# FUNCIONES AUXILIARES DE FORMATO
# ==========================================
def formatear_valor_celda(val_raw, nombre_columna=""):
    """
    Formatea automáticamente los valores de las celdas:
    - Convierte decimales a porcentajes (ej. 0.8 -> 80%).
    - Limpia valores 'nan' o nulos.
    - Formatea enteros y decimales limpios.
    """
    if pd.isna(val_raw):
        return ""

    val_str = str(val_raw).strip()
    if val_str.lower() in ["nan", "none", "null"]:
        return ""

    try:
        val_num = float(val_raw)

        es_columna_pct = any(k in nombre_columna.upper() for k in ["%", "PORCENTAJE", "AVANCE", "CUMPLIMIENTO", "PROPORTION"])

        if es_columna_pct:
            if 0 < abs(val_num) <= 1.0:
                return f"{val_num * 100:.1f}%".replace(".0%", "%")
            elif abs(val_num) > 1.0:
                return f"{val_num:.1f}%".replace(".0%", "%")
        else:
            if 0 < abs(val_num) < 1.0 and len(val_str.split('.')) > 1:
                return f"{val_num * 100:.1f}%".replace(".0%", "%")

        if val_num.is_integer():
            return str(int(val_num))
        return f"{val_num:.2f}".rstrip('0').rstrip('.')

    except ValueError:
        return val_str


def _color_bloque_superior(nombre_bloque_upper):
    """
    Devuelve el color de fondo institucional para un bloque del encabezado superior,
    según a qué familia pertenece (identidad / metas / trimestres / resultado final).
    """
    if "INFORMACIÓN DEL PROGRAMA" in nombre_bloque_upper or "INDICADORES" in nombre_bloque_upper:
        return PALETTE["guinda_dark"]
    elif "PARAMETRIZACIÓN" in nombre_bloque_upper or "METAS" in nombre_bloque_upper:
        return PALETTE["verde_dark"]
    elif "PRIMER TRIMESTRE" in nombre_bloque_upper or "TERCER TRIMESTRE" in nombre_bloque_upper:
        return PALETTE["gold_dark"]
    elif "SEGUNDO TRIMESTRE" in nombre_bloque_upper or "CUARTO TRIMESTRE" in nombre_bloque_upper:
        return PALETTE["gold"]
    elif "AVANCE" in nombre_bloque_upper or "RESULTADO" in nombre_bloque_upper:
        return PALETTE["guinda_deep"]
    return PALETTE["verde_dark"]


def _estilo_celda_status(cell_style, val_formatted, c_inf_str):
    """
    Aplica el color semántico (verde / ámbar / guinda) según el estatus de la celda,
    manteniendo la paleta institucional en vez del semáforo genérico rojo/amarillo/verde.
    """
    val_upper = val_formatted.upper()
    if "VERDE" in val_upper:
        cell_style.update({'backgroundColor': PALETTE["verde_light"], 'color': PALETTE["verde_dark"], 'fontWeight': '700', 'textAlign': 'center'})
    elif "AMARILLO" in val_upper:
        cell_style.update({'backgroundColor': PALETTE["gold_light"], 'color': PALETTE["gold_dark"], 'fontWeight': '700', 'textAlign': 'center'})
    elif "ROJO" in val_upper:
        cell_style.update({'backgroundColor': PALETTE["guinda_light"], 'color': PALETTE["guinda_dark"], 'fontWeight': '700', 'textAlign': 'center'})
    elif c_inf_str.upper() == 'NIVEL':
        cell_style.update({'textAlign': 'center', 'fontWeight': '800', 'color': PALETTE["verde_dark"]})
    elif "%" in val_formatted:
        cell_style.update({'textAlign': 'right', 'fontWeight': '700'})
    return cell_style


# ==========================================
# 1. VISTA GENERAL DE LA MIR (ALTA DIRECCIÓN)
# ==========================================
def analizar_mir_general(ruta_excel_des01):
    """
    Módulo Ejecutivo para la Matriz de Indicadores para Resultados (MIR Completa).
    - Renderiza mediante una Tabla HTML nativa con scroll y encabezados fijos (Sticky Headers).
    - Paleta institucional guinda / verde / dorado, consistente con el resto del sistema.
    """
    if not os.path.exists(ruta_excel_des01):
        return dbc.Alert(
            [
                html.H5("⚠️ Archivo Excel No Encontrado", className="font-weight-bold"),
                html.P(f"El sistema busca el archivo en la ruta: '{ruta_excel_des01}' pero no existe."),
                html.Small("Por favor, asegúrate de colocar el archivo exactamente en esa ubicación.")
            ],
            color="warning",
            className="m-3 shadow-sm"
        )

    try:
        df_headers = pd.read_excel(ruta_excel_des01, header=[1, 2], sheet_name=0)

        col_unidad = next((c for c in df_headers.columns if "Unidad Responsable" in str(c[1])), df_headers.columns[2])
        df_mir = df_headers.dropna(subset=[col_unidad]).copy()

        if df_mir.empty:
            return dbc.Alert("⚠️ No se encontraron filas válidas con datos asignados.", color="info")

        # Agrupación del Encabezado Superior (Fila 1)
        bloques_superiores = []
        bloque_actual = None
        conteo_columnas = 0

        for i, (col_superior, col_inferior) in enumerate(df_mir.columns):
            c_sup = str(col_superior).strip()

            if i <= 4 or "Unnamed:" in c_sup or c_sup == "" or c_sup.lower() == "nan":
                c_sup = "INFORMACIÓN DEL PROGRAMA"

            if c_sup != bloque_actual:
                if bloque_actual is not None:
                    bloques_superiores.append((bloque_actual, conteo_columnas))
                bloque_actual = c_sup
                conteo_columnas = 1
            else:
                conteo_columnas += 1

        if bloque_actual is not None:
            bloques_superiores.append((bloque_actual, conteo_columnas))

        th_superiores = []
        for nombre_bloque, span in bloques_superiores:
            bg_color = _color_bloque_superior(nombre_bloque.upper())

            th_superiores.append(
                html.Th(nombre_bloque.upper(), colSpan=span, style={
                    'backgroundColor': bg_color,
                    'color': '#FFFFFF',
                    'padding': '11px 10px',
                    'textAlign': 'center',
                    'fontSize': '11.5px',
                    'fontWeight': '800',
                    'border': '1px solid rgba(255, 255, 255, 0.2)',
                    'letterSpacing': '0.6px',
                    'position': 'sticky',
                    'top': '0',
                    'zIndex': '10'
                })
            )

        header_row_1 = html.Tr(th_superiores)

        # Encabezado Inferior (Fila 2)
        header_cols = []
        for c_sup, c_inf in df_mir.columns:
            header_cols.append(
                html.Th(str(c_inf).strip().upper(), style={
                    'backgroundColor': PALETTE["ink"],
                    'color': '#FFFFFF',
                    'padding': '10px 8px',
                    'fontSize': '10.5px',
                    'fontWeight': '700',
                    'textAlign': 'center',
                    'border': f'1px solid {PALETTE["ink_soft"]}',
                    'minWidth': '170px',
                    'whiteSpace': 'normal',
                    'verticalAlign': 'middle',
                    'position': 'sticky',
                    'top': '37px',
                    'zIndex': '9'
                })
            )
        header_row_2 = html.Tr(header_cols)

        # Filas de Datos
        body_rows = []
        for idx, row in df_mir.iterrows():
            cells = []
            bg_row = PALETTE["stripe"] if idx % 2 == 0 else '#FFFFFF'

            for c_sup, c_inf in df_mir.columns:
                val_raw = row[(c_sup, c_inf)]
                c_inf_str = str(c_inf).strip()
                val_formatted = formatear_valor_celda(val_raw, nombre_columna=c_inf_str)

                cell_style = {
                    'padding': '11px 13px',
                    'fontSize': '12px',
                    'fontWeight': '500',
                    'color': PALETTE["ink"],
                    'border': f'1px solid {PALETTE["line"]}',
                    'backgroundColor': bg_row,
                    'verticalAlign': 'middle',
                    'lineHeight': '1.4'
                }

                cell_style = _estilo_celda_status(cell_style, val_formatted, c_inf_str)
                cells.append(html.Td(val_formatted, style=cell_style))

            body_rows.append(html.Tr(cells))

        tabla_html = html.Table(
            [html.Thead([header_row_1, header_row_2]), html.Tbody(body_rows)],
            style={'width': '100%', 'borderCollapse': 'separate', 'borderSpacing': '0'}
        )

        return html.Div([
            html.Div([
                html.Span("📋 MATRIZ DE INDICADORES PARA RESULTADOS (MIR CONSOLIDADA)", style={"fontWeight": "800", "color": PALETTE["guinda_dark"], "fontSize": "12.5px", "letterSpacing": "0.5px"}),
                html.Span(" — VISTA GENERAL", style={"color": PALETTE["ink_soft"], "fontSize": "10.5px", "fontWeight": "700", "marginLeft": "5px"})
            ], style={"padding": "12px 16px", "backgroundColor": PALETTE["card_head_bg"], "borderBottom": f'1px solid {PALETTE["line"]}', "borderRadius": "10px 10px 0 0"}),

            html.Div(tabla_html, style={"padding": "0px", "overflowX": "auto", "overflowY": "auto", "maxHeight": "520px"})
        ], className="bg-white border shadow-sm", style={"borderRadius": "10px", "borderTop": f'4px solid {PALETTE["guinda"]}', "borderColor": PALETTE["line"]})

    except Exception as e:
        return dbc.Alert(f"❌ Error al generar vista HTML: {str(e)}", color="danger")


# ==========================================
# 2. RESUMEN DE INDICADORES POR ÁREA (COLUMNA C)
# ==========================================
def generar_tabla_resumen_area(ruta_excel_des01, unidad_responsable_seleccionada):
    """
    Genera el resumen de la MIR para una área específica filtrando por la Columna C (Unidad Responsable)
    y trayendo solo las columnas: G, I, J, M, O, P, Y, AC, AG, AK, AM, AN, AO.
    """
    if not os.path.exists(ruta_excel_des01):
        return dbc.Alert("⚠️ No se encontró el archivo de origen de datos DES01.", color="warning")

    try:
        # Cargar los 2 niveles de encabezado
        df_raw = pd.read_excel(ruta_excel_des01, header=[1, 2], sheet_name=0)

        # Columna C es el índice 2 (Unidad Responsable)
        col_unidad = df_raw.columns[2]

        # Filtrar filas donde la Columna C coincida con el Área elegida
        df_area = df_raw[df_raw[col_unidad].astype(str).str.strip().str.upper() == str(unidad_responsable_seleccionada).strip().upper()].copy()

        if df_area.empty:
            return dbc.Alert(f"ℹ️ No se encontraron indicadores registrados para el área: {unidad_responsable_seleccionada}", color="info")

        # Mapeo por posición de letra (0-indexed):
        # G=6, I=8, J=9, M=12, O=14, P=15, Y=24, AC=28, AG=32, AK=36, AM=38, AN=39, AO=40
        indices_columnas = [6, 8, 9, 12, 14, 15, 24, 28, 32, 36, 38, 39, 40]

        indices_validos = [i for i in indices_columnas if i < len(df_raw.columns)]
        cols_seleccionadas = [df_raw.columns[i] for i in indices_validos]

        # 1. ENCABEZADOS SUPERIORES (BLOQUES AGRUPADOS DINÁMICAMENTE)
        bloques_superiores = []
        bloque_actual = None
        conteo = 0

        for col_sup, _ in cols_seleccionadas:
            c_sup = str(col_sup).strip()
            if "Unnamed:" in c_sup or c_sup == "" or c_sup.lower() == "nan":
                c_sup = "INFORMACIÓN DEL PROGRAMA"

            if c_sup != bloque_actual:
                if bloque_actual is not None:
                    bloques_superiores.append((bloque_actual, conteo))
                bloque_actual = c_sup
                conteo = 1
            else:
                conteo += 1
        if bloque_actual is not None:
            bloques_superiores.append((bloque_actual, conteo))

        th_superiores = []
        for nombre_bloque, span in bloques_superiores:
            bg_color = _color_bloque_superior(nombre_bloque.upper())

            th_superiores.append(
                html.Th(nombre_bloque.upper(), colSpan=span, style={
                    'backgroundColor': bg_color,
                    'color': '#FFFFFF',
                    'padding': '11px 10px',
                    'textAlign': 'center',
                    'fontSize': '11px',
                    'fontWeight': '800',
                    'border': '1px solid rgba(255,255,255,0.2)',
                    'position': 'sticky',
                    'top': '0',
                    'zIndex': '10'
                })
            )
        row_header_1 = html.Tr(th_superiores)

        # 2. SUBENCABEZADOS DE LAS COLUMNAS ESPECÍFICAS
        th_inferiores = []
        for c_sup, c_inf in cols_seleccionadas:
            th_inferiores.append(
                html.Th(str(c_inf).strip().upper(), style={
                    'backgroundColor': PALETTE["ink"],
                    'color': '#FFFFFF',
                    'padding': '10px 8px',
                    'fontSize': '10.5px',
                    'fontWeight': '700',
                    'textAlign': 'center',
                    'border': f'1px solid {PALETTE["ink_soft"]}',
                    'minWidth': '160px',
                    'whiteSpace': 'normal',
                    'verticalAlign': 'middle',
                    'position': 'sticky',
                    'top': '37px',
                    'zIndex': '9'
                })
            )
        row_header_2 = html.Tr(th_inferiores)

        # 3. FILAS DE DATOS FORMATO FORMAL Y SEÑALIZADO
        body_rows = []
        for idx, row in df_area.iterrows():
            cells = []
            bg_row = PALETTE["stripe"] if idx % 2 == 0 else '#FFFFFF'

            for c_sup, c_inf in cols_seleccionadas:
                val_raw = row[(c_sup, c_inf)]
                c_inf_str = str(c_inf).strip()
                val_fmt = formatear_valor_celda(val_raw, nombre_columna=c_inf_str)

                cell_style = {
                    'padding': '10px 12px',
                    'fontSize': '11.5px',
                    'fontWeight': '500',
                    'color': PALETTE["ink"],
                    'border': f'1px solid {PALETTE["line"]}',
                    'backgroundColor': bg_row,
                    'verticalAlign': 'middle',
                    'lineHeight': '1.3'
                }

                cell_style = _estilo_celda_status(cell_style, val_fmt, c_inf_str)
                cells.append(html.Td(val_fmt, style=cell_style))

            body_rows.append(html.Tr(cells))

        tabla_resumen = html.Table(
            [html.Thead([row_header_1, row_header_2]), html.Tbody(body_rows)],
            style={'width': '100%', 'borderCollapse': 'separate', 'borderSpacing': '0'}
        )

        return html.Div([
            html.Div(tabla_resumen, style={"overflowX": "auto", "overflowY": "auto", "maxHeight": "480px"})
        ], className="bg-white border shadow-sm", style={"borderRadius": "10px", "borderTop": f'4px solid {PALETTE["guinda"]}', "borderColor": PALETTE["line"]})

    except Exception as e:
        return dbc.Alert(f"❌ Error al procesar el resumen por área: {str(e)}", color="danger")