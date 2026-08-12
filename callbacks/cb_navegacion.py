import json
import math
import os
import re
import sqlite3
import traceback
import urllib.request

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, Input, Output, State, dcc, html, no_update

from database import DB_GESTION, normalizar_nombre_tabla
from indicadores_pbr import calcular_indicadores_pbr

# Importaciones de componentes estéticos actualizados
from componentes_esteticos import (
    crear_tarjeta_estilo_acuerdo,
    generar_bloque_encabezado_area,
    generar_tabla_gestion,
)

# Importaciones de servicios MIR
from .servicio_mir import generar_resumen_indicadores_area

# --- Enrutador estratégico para conectar cada área con su archivo en 'areas/' ---
from analisis_estrategico import analizar_datos_estrategicos


def register_navegacion_callbacks(app):

    @app.callback(
        [
            Output("contenedor-botones-areas", "children"),
            Output("collapse-areas", "is_open"),
            Output("titulo-eje-seleccionado", "children"),
            Output("msg-placeholder-areas", "style"),
        ],
        [Input({"type": "tarjeta-eje", "index": ALL}, "n_clicks")],
        prevent_initial_call=True,
    )
    def desplegar_areas(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered or not any(x for x in n_clicks if x is not None):
            return no_update, no_update, no_update, no_update

        prop_id = ctx.triggered[0]["prop_id"]
        try:
            match_idx = re.search(r'"index":\s*(\d+)', prop_id)
            idx = int(match_idx.group(1)) if match_idx else None
        except Exception:
            return no_update, no_update, no_update, no_update

        if idx is None:
            return no_update, no_update, no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        eje_data = pd.read_sql_query(
            f"SELECT nombre FROM acuerdos WHERE id={idx}", conn
        )
        df_areas = pd.read_sql_query(
            f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn
        )
        conn.close()

        nombre_eje = (
            eje_data.iloc[0]["nombre"]
            if not eje_data.empty
            else "Eje Desconocido"
        )

        if df_areas.empty:
            return (
                html.Small(
                    "⚠️ No hay áreas asignadas a este eje.",
                    className="text-muted p-3",
                ),
                True,
                nombre_eje,
                {"display": "none"},
            )

        botones = []
        for _, area in df_areas.iterrows():
            botones.append(
                html.A(
                    [
                        html.Div(
                            [html.I(className="bi bi-folder2-open")],
                            className="area-icon-v4",
                        ),
                        html.Span(
                            area["nombre"],
                            className="ms-2 fw-600",
                            style={"fontSize": "11.5px"},
                        ),
                    ],
                    id={"type": "btn-area", "index": area["id"]},
                    className="area-row-v4",
                    style={"textDecoration": "none", "cursor": "pointer"},
                )
            )

        return botones, True, nombre_eje, {"display": "none"}

    @app.callback(
        [
            Output("contenido-area", "children"),
            Output("active-info", "data"),
            Output("resumen-kpis", "children"),
            Output("contenedor-tarjetas-acuerdos", "style"),
        ],
        [Input({"type": "btn-area", "index": ALL}, "n_clicks")],
        prevent_initial_call=True,
    )
    def mostrar_dashboard(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered or not any(x for x in n_clicks if x is not None):
            return no_update, no_update, no_update, no_update

        try:
            trigger_prop = ctx.triggered[0]["prop_id"]
            if not trigger_prop or "." not in trigger_prop:
                return no_update, no_update, no_update, no_update

            dict_str = trigger_prop.split(".")[0]
            dict_val = json.loads(dict_str)
            idx = dict_val.get("index")
        except Exception as parse_err:
            return (
                dbc.Alert(
                    f"Error de selección: {str(parse_err)}", color="danger"
                ),
                no_update,
                "",
                no_update
            )

        if idx is None:
            return no_update, no_update, no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        query = """
            SELECT a.nombre as area_nom, ac.nombre as eje_nom 
            FROM areas a 
            JOIN acuerdos ac ON a.acuerdo_id = ac.id 
            WHERE a.id=?
        """
        area_info = pd.read_sql_query(query, conn, params=(idx,))

        if area_info.empty:
            conn.close()
            return (
                dbc.Alert(
                    "Área no registrada en la base de datos.", color="warning"
                ),
                no_update,
                "",
                no_update
            )

        nombre_completo = area_info.iloc[0]["area_nom"]
        nombre_eje = area_info.iloc[0]["eje_nom"]
        tabla = normalizar_nombre_tabla(nombre_completo)

        # Separar clave y nombre
        match_clave = re.match(r"^([\d\.]+)\s*(.*)", nombre_completo)
        clave_area = match_clave.group(1) if match_clave else ""
        nombre_area = match_clave.group(2) if match_clave else nombre_completo

        tablas_existentes = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table';", conn
        )["name"].tolist()

        # Determinar icono segun area
        icono_area = "ti ti-briefcase"
        if "psicologia" in nombre_completo.lower(): icono_area = "ti ti-brain"
        elif "seguridad" in nombre_completo.lower(): icono_area = "ti ti-shield"
        elif "obras" in nombre_completo.lower(): icono_area = "ti ti-building"
        elif "dif" in nombre_completo.lower(): icono_area = "ti ti-heart"

        if tabla not in tablas_existentes:
            conn.close()
            encabezado = generar_bloque_encabezado_area(nombre_eje, clave_area, nombre_area, icono_area)
            return html.Div(
                [
                    encabezado,
                    dbc.Alert(
                        "Aún no se han cargado datos para esta área administrativa.",
                        color="info",
                        className="mt-4",
                    ),
                ]
            ), {"tabla": tabla, "id": idx}, "", no_update

        try:
            try:
                df = pd.read_sql_query(f'SELECT rowid, * FROM "{tabla}"', conn)
            except Exception:
                df = pd.read_sql_query(f'SELECT * FROM "{tabla}"', conn)
                if "rowid" not in df.columns:
                    df.insert(0, "rowid", range(1, len(df) + 1))

            conn.close()

            # --- SERVICIO MIR ORIGINAL ---
            try:
                resumen_mir = generar_resumen_indicadores_area(nombre_completo, df)
            except TypeError:
                try:
                    resumen_mir = generar_resumen_indicadores_area(nombre_completo)
                except Exception:
                    resumen_mir = html.Div()
            except Exception:
                resumen_mir = html.Div()

            # --- VINCULACIÓN CON EL ENRUTADOR DE ANÁLISIS POR ÁREA ---
            analisis_especifico = analizar_datos_estrategicos(tabla, df)
            if analisis_especifico is None or isinstance(analisis_especifico, dbc.Alert):
                analisis_especifico = analizar_datos_estrategicos(nombre_completo, df)

            if isinstance(analisis_especifico, dbc.Alert) and "aún no se ha configurado" in analisis_especifico.children:
                analisis_especifico = html.Div()

            # Encabezado V4
            encabezado_v4 = generar_bloque_encabezado_area(nombre_eje, clave_area, nombre_area, icono_area)

            # --- ESTRUCTURA DE LA TABLA DE INDICADORES DETALLADOS CON ESTILOS OPTIMIZADOS ---
            total_registros = len(df)
            
            total_invertido_str = "$ 0.00"
            for col_cand in df.columns:
                if any(term in col_cand.lower() for term in ["inversion", "monto", "costo", "total"]):
                    try:
                        val_sum = pd.to_numeric(df[col_cand], errors="coerce").sum()
                        if val_sum > 0:
                            total_invertido_str = f"$ {val_sum:,.2f}"
                            break
                    except Exception:
                        pass

            componente_tabla_detallada = html.Div(
                [
                    # Inyección de estilos CSS optimizados para ajustar títulos largos, saltos de línea y celdas compactas
                    html.Div(
                        children=dcc.Markdown(
                            """
<style>
.compact-table-wrapper table {
    width: 100% !important;
    table-layout: auto !important;
}
.compact-table-wrapper th {
    white-space: normal !important;
    word-break: break-word !important;
    text-align: center !important;
    padding: 8px 6px !important;
    font-size: 10.5px !important;
    line-height: 1.2 !important;
}
.compact-table-wrapper td {
    padding: 5px 6px !important;
    font-size: 11px !important;
}
</style>
                            """,
                            dangerously_allow_html=True
                        ),
                        style={"display": "none"}
                    ),
                    html.Div(
                        className="table-card mt-5",
                        style={
                            "background": "#FFFFFF",
                            "border": "1px solid #E3DDD2",
                            "borderRadius": "8px",
                            "position": "relative",
                            "overflow": "hidden",
                        },
                        children=[
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "0",
                                    "left": "0",
                                    "right": "0",
                                    "height": "3px",
                                    "background": "#7A1E3D",
                                    "zIndex": "2",
                                }
                            ),
                            # Cabecera interactiva para colapsar/expandir
                            html.Div(
                                id="btn-toggle-tabla-indicadores",
                                className="table-title-row",
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "space-between",
                                    "padding": "18px 22px",
                                    "cursor": "pointer",
                                    "userSelect": "none",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "10px",
                                        },
                                        children=[
                                            html.I(
                                                className="ti ti-table",
                                                style={
                                                    "color": "#7A1E3D",
                                                    "fontSize": "18px",
                                                },
                                            ),
                                            html.Div(
                                                "Registro de indicadores detallados",
                                                style={
                                                    "fontFamily": (
                                                        "'Playfair Display',"
                                                        " serif"
                                                    ),
                                                    "fontWeight": "700",
                                                    "fontSize": "16px",
                                                    "letterSpacing": ".03em",
                                                    "textTransform": (
                                                        "uppercase"
                                                    ),
                                                    "color": "#5A1530",
                                                },
                                            ),
                                        ],
                                    ),
                                    html.I(
                                        className="ti ti-chevron-down",
                                        style={
                                            "color": "#6B625C",
                                            "fontSize": "16px",
                                        },
                                    ),
                                ],
                            ),
                            # Acordeón con la clase compacta y ajuste de cabeceras integradas
                            dbc.Collapse(
                                html.Div(
                                    className="compact-table-wrapper",
                                    style={
                                        "maxHeight": "310px",
                                        "overflowY": "auto",
                                        "overflowX": "auto",
                                        "width": "100%",
                                        "borderTop": "1px solid #E3DDD2",
                                    },
                                    children=[generar_tabla_gestion(df)],
                                ),
                                id="collapse-tabla-indicadores",
                                is_open=False,
                            ),
                            html.Div(
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "space-between",
                                    "padding": "12px 22px",
                                    "borderTop": "1px solid #E3DDD2",
                                    "fontSize": "11px",
                                    "color": "#9B928C",
                                    "background": "#FFF",
                                },
                                children=[
                                    html.Span(f"{total_registros} registros"),
                                    html.Span(
                                        [
                                            "Total invertido: ",
                                            html.B(
                                                total_invertido_str,
                                                style={"color": "#0C5148"},
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    )
                ]
            )

            contenido = html.Div(
                [
                    encabezado_v4,
                    html.Div(
                        "Evidencia analítica de impacto social directo asociada a los objetivos institucionales.",
                        className="section-desc"
                    ),
                    analisis_especifico,
                    componente_tabla_detallada,
                ]
            )

            return contenido, {"tabla": tabla, "id": idx}, "", no_update

        except Exception as e:
            traceback.print_exc()
            if "conn" in locals():
                conn.close()
            error_msg = (
                f"{type(e).__name__}: {str(e)}"
                if str(e)
                else type(e).__name__
            )
            return (
                dbc.Alert(
                    f"Error interno al cargar la tabla '{tabla}':"
                    f" {error_msg}",
                    color="danger",
                ),
                no_update,
                "",
                no_update
            )

    @app.callback(
        Output("collapse-tabla-indicadores", "is_open"),
        Input("btn-toggle-tabla-indicadores", "n_clicks"),
        State("collapse-tabla-indicadores", "is_open"),
        prevent_initial_call=True,
    )
    def alternar_tabla_indicadores(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # El callback 'volver_a_ejes' se mantiene por compatibilidad si existiera otro botón, 
    # pero ya no se ocultan los ejes al seleccionar un área.
    @app.callback(
        [
            Output("contenido-area", "children", allow_duplicate=True),
            Output("resumen-kpis", "children", allow_duplicate=True),
            Output("collapse-areas", "is_open", allow_duplicate=True),
            Output("contenedor-tarjetas-acuerdos", "style", allow_duplicate=True),
        ],
        Input("btn-volver-ejes", "n_clicks"),
        prevent_initial_call=True,
    )
    def volver_a_ejes(n):
        if n:
            return "", "", False, no_update
        return no_update, no_update, no_update, no_update