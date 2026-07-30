import json
import math
import os
import re
import sqlite3
import urllib.request

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, dcc, html, no_update

from database import DB_GESTION, normalizar_nombre_tabla
from indicadores_pbr import calcular_indicadores_pbr
from visualizaciones import generar_tablero_impacto, seccion_impacto_layout

# Importaciones relativas dentro de la carpeta callbacks
from .componentes_navegacion import (
    DICCIONARIO_AREAS,
    DICCIONARIO_ICONOS_ACUERDOS,
    TAMANO_PAGINA,
    construir_tabla_estilo_cards,
    diseñar_tarjeta_pbr,
)
from .servicio_mir import generar_resumen_indicadores_area


def register_navegacion_callbacks(app):

    @app.callback(
        Output("contenedor-tarjetas-acuerdos", "children"),
        Input("contenedor-tarjetas-acuerdos", "id"),
    )
    def cargar_acuerdos(_):
        conn = sqlite3.connect(DB_GESTION)
        try:
            df = pd.read_sql_query("SELECT * FROM acuerdos", conn)
        except Exception:
            df = pd.DataFrame()

        if df.empty:
            ejes_defecto = [
                (1, "GOBIERNO PARTICIPATIVO Y TRANSFORMADOR"),
                (2, "BIENESTAR Y PROSPERIDAD"),
                (3, "DESARROLLO ECONÓMICO Y CULTURAL"),
                (4, "DESARROLLO SOSTENIBLE E INFRAESTRUCTURA"),
            ]
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS acuerdos (id INTEGER PRIMARY KEY, nombre TEXT)"
            )
            cursor.executemany(
                "INSERT OR IGNORE INTO acuerdos (id, nombre) VALUES (?, ?)",
                ejes_defecto,
            )
            conn.commit()
            df = pd.read_sql_query("SELECT * FROM acuerdos", conn)

        conn.close()

        tarjetas = []
        for _, f in df.iterrows():
            id_acuerdo = int(f["id"])
            nombre_acuerdo = f["nombre"]
            porcentaje_base = (
                85
                if id_acuerdo == 1
                else (70 if id_acuerdo == 2 else (90 if id_acuerdo == 3 else 60))
            )
            icono_clase = DICCIONARIO_ICONOS_ACUERDOS.get(
                id_acuerdo, "bi bi-folder"
            )

            fig_dona = go.Figure(
                go.Pie(
                    values=[porcentaje_base, 100 - porcentaje_base],
                    hole=0.72,
                    marker_colors=["#691c32", "#e5e7eb"],
                    textinfo="none",
                    hoverinfo="none",
                )
            )
            fig_dona.update_layout(
                showlegend=False,
                margin=dict(t=0, b=0, l=0, r=0),
                width=75,
                height=75,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )

            tarjetas.append(
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(
                                        className=icono_clase,
                                        style={
                                            "position": "absolute",
                                            "fontSize": "1.3rem",
                                            "color": "#691c32",
                                            "zIndex": "10",
                                        },
                                    ),
                                    dcc.Graph(
                                        figure=fig_dona,
                                        config={"displayModeBar": False},
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                    "position": "relative",
                                    "marginBottom": "15px",
                                },
                            ),
                            html.P(
                                nombre_acuerdo,
                                className="text-center mb-2 font-weight-bold",
                                style={
                                    "fontSize": "0.78rem",
                                    "color": "#1f2937",
                                    "lineHeight": "1.4",
                                },
                            ),
                            html.H6(
                                f"{porcentaje_base}%",
                                className="text-center font-weight-bold",
                                style={
                                    "color": "#691c32",
                                    "fontSize": "0.9rem",
                                    "margin": "0",
                                },
                            ),
                            dbc.Button(
                                "",
                                id={
                                    "type": "btn-acuerdo",
                                    "index": id_acuerdo,
                                },
                                style={
                                    "position": "absolute",
                                    "top": "0",
                                    "left": "0",
                                    "width": "100%",
                                    "height": "100%",
                                    "opacity": "0",
                                    "cursor": "pointer",
                                    "zIndex": "20",
                                },
                            ),
                        ],
                        className="p-4 bg-white border text-center position-relative h-100 shadow-sm",
                        style={
                            "borderRadius": "18px",
                            "borderColor": "#e5e7eb",
                        },
                    ),
                    width=12,
                    sm=6,
                    md=3,
                    className="mb-4",
                )
            )
        return tarjetas

    @app.callback(
        [
            Output("collapse-areas", "is_open"),
            Output("contenedor-botones-areas", "children"),
        ],
        [Input({"type": "btn-acuerdo", "index": ALL}, "n_clicks")],
        prevent_initial_call=True,
    )
    def desplegar_areas(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update

        prop_id = ctx.triggered[0]["prop_id"]
        if "value" in prop_id or not any(x for x in n_clicks if x is not None):
            return no_update, no_update

        try:
            idx = json.loads(prop_id.split(".")[0])["index"]
        except (json.JSONDecodeError, KeyError, IndexError):
            return no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        df = pd.read_sql_query(
            f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn
        )
        conn.close()

        if df.empty:
            return True, html.Small(
                "⚠️ No hay áreas asignadas a este eje estratégico todavía.",
                className="text-muted p-2",
            )

        def extraer_clave_orden(nombre):
            match = re.match(r"^([\d\.]+)", str(nombre).strip())
            if match:
                partes = match.group(1).split(".")
                return [int(p) for p in partes if p.isdigit()]
            return [999]

        df["orden_num"] = df["nombre"].apply(extraer_clave_orden)
        df = df.sort_values(by="orden_num").drop(columns=["orden_num"])

        botones = []
        for _, a in df.iterrows():
            nombre_area = a["nombre"]
            match_clave = re.match(r"^([\d\.]+)\s*(.*)", nombre_area)
            if match_clave:
                num_tag = match_clave.group(1)
                texto_tag = match_clave.group(2)
            else:
                num_tag = "•"
                texto_tag = nombre_area

            btn_content = html.Div(
                [
                    html.Span(
                        num_tag,
                        style={
                            "backgroundColor": "#691C32",
                            "color": "#FFFFFF",
                            "padding": "3px 8px",
                            "borderRadius": "8px",
                            "fontSize": "0.72rem",
                            "fontWeight": "700",
                            "marginRight": "8px",
                        },
                    ),
                    html.Span(
                        texto_tag.upper(),
                        style={
                            "fontSize": "0.75rem",
                            "fontWeight": "600",
                            "color": "#334155",
                            "letterSpacing": "0.3px",
                        },
                    ),
                ],
                className="d-flex align-items-center",
            )

            botones.append(
                dbc.Button(
                    btn_content,
                    id={"type": "btn-area", "index": a["id"]},
                    color="light",
                    className="m-1 shadow-sm border",
                    style={
                        "borderRadius": "10px",
                        "border": "1px solid #CBD5E1",
                        "backgroundColor": "#FFFFFF",
                        "padding": "6px 14px",
                    },
                )
            )

        return True, html.Div(
            botones,
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "6px",
                "padding": "6px 0",
            },
        )

    # --- CALLBACK PRINCIPAL CON RENDERIZADO DIRECTO ---
    @app.callback(
        [
            Output("contenido-area", "children"),
            Output("active-info", "data"),
            Output("resumen-kpis", "children"),
        ],
        [Input({"type": "btn-area", "index": ALL}, "n_clicks")],
        prevent_initial_call=True,
    )
    def mostrar_dashboard(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered or not any(x for x in n_clicks if x is not None):
            return no_update, no_update, no_update

        try:
            prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
            idx = json.loads(prop_id)["index"]
        except Exception:
            return no_update, no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        area_data = pd.read_sql_query(
            "SELECT nombre FROM areas WHERE id=?", conn, params=(idx,)
        )

        if area_data.empty:
            conn.close()
            return (
                dbc.Alert(
                    "Área no registrada en la base de datos.", color="warning"
                ),
                no_update,
                "",
            )

        nombre_area = area_data.iloc[0]["nombre"]
        tabla = normalizar_nombre_tabla(nombre_area)

        info_est = DICCIONARIO_AREAS.get(
            tabla,
            {
                "resumen": "Área operativa integrada en los acuerdos del Plan Municipal.",
                "objetivo": "Seguimiento y evaluación continua de los indicadores sectoriales.",
            },
        )

        tablas_existentes = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table';", conn
        )["name"].tolist()

        if tabla not in tablas_existentes:
            conn.close()
            aviso = dbc.Alert(
                [
                    html.H5(
                        "⚠️ Tabla vacía o no sincronizada",
                        className="alert-heading",
                    ),
                    html.P(
                        f"El área '{nombre_area}' está registrada pero aún no contiene datos importados en la tabla SQLite '{tabla}'."
                    ),
                    html.Hr(),
                    html.Small(
                        "Utiliza el botón de administración en el encabezado para cargar el Excel correspondiente."
                    ),
                ],
                color="warning",
            )
            return aviso, {"tabla": tabla, "id": idx}, ""

        try:
            df = pd.read_sql_query(f'SELECT rowid, * FROM "{tabla}"', conn)
            conn.close()

            datos_pbr_raw = calcular_indicadores_pbr(df)
            resumen_cards = diseñar_tarjeta_pbr(datos_pbr_raw)

            bloque_resumen = dbc.Alert(
                [
                    html.H5(
                        f"📌 RESUMEN ESTRATÉGICO: {nombre_area}",
                        className="alert-heading fw-bold mb-2",
                        style={"fontSize": "0.95rem", "color": "#691c32"},
                    ),
                    html.P(
                        info_est["resumen"],
                        className="mb-2 text-dark",
                        style={"fontSize": "0.85rem", "fontWeight": "500"},
                    ),
                    html.Hr(style={"margin": "8px 0", "borderColor": "#cbd5e1"}),
                    html.Div(
                        [
                            html.Strong("🎯 OBJETIVO GENERAL: ", style={"color": "#1ca2a9"}),
                            html.Span(info_est['objetivo'], className="text-secondary"),
                        ],
                        style={"fontSize": "0.8rem"},
                    ),
                ],
                color="light",
                className="mt-2 mb-3 shadow-sm border",
                style={
                    "borderLeft": "5px solid #691c32",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "10px"
                },
            )

            store_pagina = dcc.Store(id="store-pagina-actual", data=1)
            resumen_mir_excel = generar_resumen_indicadores_area(nombre_area)
            
            seccion_tabla_contraible = html.Div(
                [
                    dbc.Button(
                        "📋 Ver Tabla de Registros Detallados (Base de Datos)",
                        id="btn-collapse-tabla",
                        className="mb-3 w-100 text-start fw-bold shadow-sm",
                        color="light",
                        style={
                            "borderColor": "#cbd5e1",
                            "color": "#691c32",
                            "borderRadius": "10px",
                            "backgroundColor": "#ffffff"
                        },
                    ),
                    dbc.Collapse(
                        html.Div(
                            id="contenedor-tabla-paginada",
                            className="bg-white p-3 border shadow-sm",
                            style={"borderRadius": "10px", "borderColor": "#e5e7eb"}
                        ),
                        id="collapse-tabla-registros",
                        is_open=False,
                    ),
                ],
                className="mt-4 mb-4"
            )

            contenido = html.Div([
                store_pagina,
                html.Div(
                    [
                        html.H2(
                            f"📊 {nombre_area}",
                            className="m-0",
                            style={"fontSize": "1.1rem", "fontWeight": "700", "color": "#691c32"},
                        ),
                    ],
                    className="p-3 mb-3 bg-white shadow-sm",
                    style={
                        "borderTop": "5px solid #1ca2a9",
                        "borderLeft": "1px solid #dee2e6",
                        "borderRight": "1px solid #dee2e6",
                        "borderBottom": "1px solid #dee2e6",
                        "borderRadius": "10px"
                    },
                ),
                bloque_resumen,
                resumen_mir_excel,
                seccion_impacto_layout(),
                seccion_tabla_contraible,
            ])
            return contenido, {"tabla": tabla, "id": idx}, resumen_cards
        except Exception as e:
            if "conn" in locals():
                conn.close()
            return (
                dbc.Alert(
                    f"Error al estructurar el tablero: {e}", color="danger"
                ),
                no_update,
                "",
            )

    @app.callback(
        Output("collapse-tabla-registros", "is_open"),
        [Input("btn-collapse-tabla", "n_clicks")],
        [State("collapse-tabla-registros", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_collapse_tabla(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("store-pagina-actual", "data"),
        [
            Input("btn-pag-inicio", "n_clicks"),
            Input("btn-pag-prev", "n_clicks"),
            Input("btn-pag-next", "n_clicks"),
            Input("btn-pag-fin", "n_clicks"),
        ],
        [State("store-pagina-actual", "data"), State("active-info", "data")],
        prevent_initial_call=True,
    )
    def cambiar_pagina(
        btn_inicio, btn_prev, btn_next, btn_fin, pag_actual, active_info
    ):
        ctx = dash.callback_context
        if not ctx.triggered or not active_info:
            return no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        conn = sqlite3.connect(DB_GESTION)
        df_count = pd.read_sql_query(
            f'SELECT COUNT(*) as total FROM "{active_info["tabla"]}"', conn
        )
        conn.close()

        total_registros = df_count.iloc[0]["total"]
        total_paginas = (
            math.ceil(total_registros / TAMANO_PAGINA)
            if total_registros > 0
            else 1
        )

        if trigger_id == "btn-pag-inicio":
            return 1
        elif trigger_id == "btn-pag-prev":
            return max(1, pag_actual - 1)
        elif trigger_id == "btn-pag-next":
            return min(total_paginas, pag_actual + 1)
        elif trigger_id == "btn-pag-fin":
            return total_paginas

        return pag_actual

    @app.callback(
        Output("contenedor-tabla-paginada", "children"),
        [
            Input("store-pagina-actual", "data"),
            Input("contenido-area", "children"),
            Input("active-info", "data")
        ],
    )
    def renderizar_tabla_paginada(pag_actual, contenido_area_children, active_info):
        if not active_info or "tabla" not in active_info:
            return no_update

        conn = sqlite3.connect(DB_GESTION)
        try:
            df = pd.read_sql_query(
                f'SELECT rowid, * FROM "{active_info["tabla"]}"', conn
            )
            conn.close()

            ctx = dash.callback_context
            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
            
            pagina_a_mostrar = 1 if triggered_id == "contenido-area" else (pag_actual or 1)

            return construir_tabla_estilo_cards(
                df, pagina_actual=pagina_a_mostrar
            )
        except Exception as e:
            if "conn" in locals():
                conn.close()
            return dbc.Alert(f"No se pudieron cargar los datos de la tabla: {e}", color="danger")

    @app.callback(
        Output("contenedor-graficas-impacto", "children"),
        Input("contenido-area", "children"),
        State("active-info", "data"),
    )
    def actualizar_graficas(_, info):
        if not info:
            return no_update
        conn = sqlite3.connect(DB_GESTION)
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{info["tabla"]}"', conn)
            conn.close()
            return generar_tablero_impacto(df, nombre_tabla=info["tabla"])
        except Exception:
            conn.close()
            return no_update

    # --- CALLBACK PARA LA DESCARGA DEL ARCHIVO ORIGINAL DES01_CHU_02_2026.xlsx ---
    @app.callback(
        Output("download-excel-mir-original", "data"),
        Input("btn-descargar-mir-original", "n_clicks"),
        prevent_initial_call=True,
    )
    def descargar_matriz_mir_original(n_clicks):
        if not n_clicks:
            return no_update

        nombre_archivo = "DES01_CHU_02_2026.xlsx"

        # 1. Intentar buscar el archivo original de forma local en el servidor (ej. carpeta actual o una subcarpeta de cargas)
        rutas_posibles = [
            nombre_archivo,
            os.path.join("uploads", nombre_archivo),
            os.path.join("data", nombre_archivo)
        ]
        
        for ruta in rutas_posibles:
            if os.path.exists(ruta):
                return dcc.send_file(ruta)

        # 2. Si manejas el enlace de Google Drive directamente, puedes transformar el link para forzar la descarga de exportación:
        # Link proporcionado: https://docs.google.com/spreadsheets/d/11jBjOTf6nqwGzaVMj4AQyR4ApYT2MaYJ/edit?...
        file_id = "11jBjOTf6nqwGzaVMj4AQyR4ApYT2MaYJ"
        url_descarga_drive = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

        try:
            # Descargamos temporalmente el archivo desde Google Drive para enviarlo al navegador del usuario
            req = urllib.request.Request(url_descarga_drive, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                contenido_archivo = response.read()
            
            return dict(content=contenido_archivo, filename=nombre_archivo)
        except Exception as e:
            # Si falla la red o el archivo local no existe, retornamos un DataFrame de aviso como respaldo de emergencia
            df_error = pd.DataFrame({"Error": [f"No se pudo descargar el archivo original '{nombre_archivo}': {str(e)}"]})
            return dcc.send_data_frame(df_error.to_excel, "Error_Descarga.xlsx", index=False)