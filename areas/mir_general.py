# areas/mir_general.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dash_table
import os

def analizar_mir_general(ruta_excel_des01):
    """
    Módulo Ejecutivo de Alta Dirección para la Matriz de Indicadores para Resultados (MIR).
    - Procesa el archivo DES01 directamente en formato Excel (.xlsx).
    - Remueve por completo las cajas de filtros para corregir la estética superior y los huecos en blanco.
    - Unifica cromáticamente todo el bloque inicial en Guinda Institucional.
    - Mantiene inmovilizados los encabezados superiores de forma fluida.
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
        # 1. Cargar el Excel capturando los dos niveles de encabezado
        df_headers = pd.read_excel(ruta_excel_des01, header=[1, 2], sheet_name=0)
        
        # Estructuración limpia de los dos niveles de títulos
        nuevas_columnas = []
        for col_superior, col_inferior in df_headers.columns:
            c_sup = str(col_superior).strip()
            c_inf = str(col_inferior).strip()
            
            # Unificamos bajo el mismo concepto superior para forzar la fusión cromática
            if "Unnamed:" in c_sup or c_sup == "" or c_sup == "nan":
                c_sup = "Información del programa"
                
            nuevas_columnas.append((c_sup, c_inf))
            
        df_headers.columns = pd.MultiIndex.from_tuples(nuevas_columnas)

        # Buscar la columna Unidad Responsable de forma flexible
        col_unidad_tupla = next((c for c in df_headers.columns if "Unidad Responsable" in c[1]), None)
        if not col_unidad_tupla:
            return dbc.Alert(f"❌ Error de Estructura: No se encontró la columna 'Unidad Responsable'.", color="danger")
            
        # Limpieza de filas vacías
        df_mir = df_headers.dropna(subset=[col_unidad_tupla]).copy()
        if df_mir.empty:
            return dbc.Alert("⚠️ No se encontraron filas válidas con una 'Unidad Responsable' asignada.", color="info")
        
        col_semaforos_tubras = [c for c in df_mir.columns if 'Semáforo' in c[1]]

        # 2. CONSTRUCCIÓN DE COLUMNAS PARA LA DATATABLE
        columnas_multi = []
        for c_sup, c_inf in df_mir.columns:
            columnas_multi.append({
                "name": [c_sup, c_inf],
                "id": c_inf
            })

        # Aplanamos los datos mapeándolos directo al ID de la Fila 2
        datos_aplanados = []
        for _, row in df_mir.iterrows():
            dict_fila = {}
            for c_sup, c_inf in df_mir.columns:
                dict_fila[c_inf] = row[(c_sup, c_inf)]
            datos_aplanados.append(dict_fila)

        # 3. PALETA CROMÁTICA COMPLETA POR BLOQUES DE ENCABEZADO
        estilos_encabezados_bloques = []
        for c_sup, c_inf in df_mir.columns:
            bg_color = "#e2e8f0" 
            text_color = "#1a202c"
            
            if "Información del programa" in c_sup or "Indicadores" in c_sup:
                bg_color = "#691c32"  # Guinda Institucional exacto
                text_color = "white"
            elif "Parametrización" in c_sup:
                bg_color = "#1e3a8a"  # Azul Rey Corporativo
                text_color = "white"
            elif "Primer Trimestre" in c_sup:
                bg_color = "#f1f5f9"
                text_color = "#1e293b"
            elif "Segundo Trimestre" in c_sup:
                bg_color = "#cbd5e1"
                text_color = "#1e293b"
            elif "Tercer Trimestre" in c_sup:
                bg_color = "#f1f5f9"
                text_color = "#1e293b"
            elif "Cuarto Trimestre" in c_sup:
                bg_color = "#cbd5e1"
                text_color = "#1e293b"
            elif "Avance anual" in c_sup or "Avance Anual" in c_sup:
                bg_color = "#0f172a"  # Gris Oscuro Pizarra
                text_color = "white"

            estilos_encabezados_bloques.append({
                'if': {'column_id': c_inf},
                'backgroundColor': bg_color,
                'color': text_color,
                'border': '1px solid #dee2e6' # Mantiene la cuadrícula limpia
            })

        # 4. CONFIGURACIÓN E INTEGRACIÓN DE LA TABLA LIMPIA Y REESTRUCTURADA
        tabla_mir = dash_table.DataTable(
            data=datos_aplanados,
            columns=columnas_multi,
            merge_duplicate_headers=True, # Fusiona celdas superiores del mismo bloque
            style_as_list_view=False,
            page_size=45,
            sort_action="native",         # Conservamos la ordenación de columnas ya que es muy útil
            
            # Remoción de filtros nativos para corregir la estética
            filter_action="none",         
            
            # Fijación multidireccional segura
            fixed_rows={'headers': True},
            fixed_columns={'headers': True, 'data': 1},
            
            style_table={
                'overflowX': 'auto',
                'overflowY': 'auto',
                'maxHeight': '480px',
                'minWidth': '100%'
            },
            style_header={
                'fontWeight': 'bold',
                'fontSize': '10.5px',
                'padding': '12px 10px',
                'textAlign': 'center',
                'border': '1px solid #cbd5e0'
            },
            style_header_conditional=estilos_encabezados_bloques,
            
            style_cell={
                'padding': '10px 14px',
                'fontSize': '11px',
                'color': '#2d3748',
                'fontFamily': 'Helvetica, Arial, sans-serif',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '170px',
                'maxWidth': '320px',
                'backgroundColor': 'white',
                'border': '1px solid #e2e8f0'
            },
            style_cell_conditional=[
                {'if': {'column_id': c[1]}, 'textAlign': 'left'} for c in df_mir.columns
            ],
            
            # Semáforos condicionales trimestrales en base a los datos
            style_data_conditional=[
                {
                    'if': {
                        'column_id': c[1],
                        'filter_query': f'{{{c[1]}}} contains "VERDE"'
                    },
                    'backgroundColor': '#c6f6d5', 'color': '#22543d', 'fontWeight': 'bold'
                } for c in col_semaforos_tubras
            ] + [
                {
                    'if': {
                        'column_id': c[1],
                        'filter_query': f'{{{c[1]}}} contains "AMARILLO"'
                    },
                    'backgroundColor': '#feebc8', 'color': '#744210', 'fontWeight': 'bold'
                } for c in col_semaforos_tubras
            ] + [
                {
                    'if': {
                        'column_id': c[1],
                        'filter_query': f'{{{c[1]}}} contains "ROJO"'
                    },
                    'backgroundColor': '#fed7d7', 'color': '#742a2a', 'fontWeight': 'bold'
                } for c in col_semaforos_tubras
            ],
        )

        return html.Div([
            html.Div([
                html.Span("📋 MATRIZ DE INDICADORES PARA RESULTADOS (MIR CONSOLIDADA)", style={"fontWeight": "800", "color": "#691c32", "fontSize": "12px"}),
                html.Span(" — VISTA EJECUTIVA CONSOLIDAD", style={"color": "#718096", "fontSize": "10px", "fontWeight": "600", "marginLeft": "5px"})
            ], style={"padding": "12px 16px", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "borderRadius": "10px 10px 0 0"}),
            
            html.Div(tabla_mir, style={"padding": "12px"})
        ], className="bg-white border shadow-sm", style={"borderRadius": "10px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error crítico al procesar la MIR con Doble Encabezado: {str(e)}", color="danger")
