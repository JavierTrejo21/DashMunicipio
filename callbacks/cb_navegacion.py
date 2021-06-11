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
                (5, "IGUALDAD Y DERECHOS HUMANOS"),
                (6, "GOBIERNO TECNOLÓGICO Y DIGITAL"),
                (7, "TRANSPARENCIA Y RENDICIÓN DE CUENTAS"),
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

        iconos_disponibles = [
            "bi bi-diagram-3-fill",
            "bi bi-rocket-takeoff-fill",
            "bi bi-rocket-fill",
            "bi bi-lightbulb-fill",
            "bi bi-lightbulb",
            "bi bi-display",
            "bi bi-folder-fill"
        ]

        config_elementos = {}
        for idx, row in df.iterrows():
            id_acuerdo = int(row["id"])
            icono_asignado = iconos_disponibles[(id_acuerdo - 1) % len(iconos_disponibles)]
            config_elementos[id_acuerdo] = {
                "sub": "Seguimiento estratégico y evaluación de indicadores...",
                "icon": icono_asignado,
                "titulo": row["nombre"]
            }

        def crear_tarjeta_estilo(id_acuerdo, conf, porcentaje_base, posicion="centro"):
            if posicion == "izq":
                borde_estilo = {
                    "borderLeft": "6px solid #781d37",
                    "borderTop": "1px solid rgba(255, 255, 255, 1)",
                    "borderRight": "1px solid rgba(255, 255, 255, 1)",
                    "borderBottom": "1px solid rgba(255, 255, 255, 1)",
                }
            elif posicion == "der":
                borde_estilo = {
                    "borderRight": "6px solid #781d37",
                    "borderTop": "1px solid rgba(255, 255, 255, 1)",
                    "borderLeft": "1px solid rgba(255, 255, 255, 1)",
                    "borderBottom": "1px solid rgba(255, 255, 255, 1)",
                }
            else:
                borde_estilo = {
                    "borderRight": "6px solid #781d37",
                    "borderLeft": "6px solid #781d37",
                    "borderTop": "1px solid rgba(255, 255, 255, 1)",
                    "borderBottom": "1px solid rgba(255, 255, 255, 1)",
                }

            estilos_base = {
                "borderRadius": "14px", 
                "backgroundColor": "rgba(255, 255, 255, 0.9)",
                "boxShadow": "0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05)",
                "cursor": "pointer", 
                "width": "100%", 
                "maxWidth": "440px", 
                "height": "95px", 
                "margin": "0 auto",
                "padding": "10px"
            }
            estilos_base.update(borde_estilo)

            return html.Div(
                [
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.I(className=conf["icon"], style={"fontSize": "1.1rem", "color": "#781d37"})
                            ], style={
                                "width": "42px", "height": "42px", "borderRadius": "50%", 
                                "backgroundColor": "#ffffff", 
                                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.06)",
                                "display": "flex", "alignItems": "center", "justifyContent": "center", "margin": "auto"
                            })
                        ], className="col-2 d-flex align-items-center justify-content-center"),
                        dbc.Col([
                            html.H6(conf["titulo"], className="mb-1 fw-bold text-dark", style={"fontSize": "0.75rem", "lineHeight": "1.2", "letterSpacing": "0.3px"}),
                            html.P(conf["sub"], className="text-muted mb-2 text-truncate", style={"fontSize": "0.62rem"}),
                            html.Div([
                                html.Div(style={
                                    "width": f"{porcentaje_base}%", "height": "5px", 
                                    "background": "linear-gradient(90deg, #1ca2a9 0%, #00b4d8 100%)", 
                                    "borderRadius": "4px",
                                    "boxShadow": "0 2px 4px rgba(28, 162, 169, 0.3)"
                                })
                            ], style={"width": "100%", "backgroundColor": "#e2e8f0", "borderRadius": "4px", "overflow": "hidden"})
                        ], className="col-10")
                    ], className="g-0 align-items-center"),
                    dbc.Button(
                        "",
                        id={"type": "btn-acuerdo", "index": id_acuerdo},
                        style={"position": "absolute", "top": "0", "left": "0", "width": "100%", "height": "100%", "opacity": "0", "cursor": "pointer", "zIndex": "20"},
                    ),
                ],
                className="bg-white position-relative mb-2",
                style=estilos_base,
            )

        lista_ids = list(config_elementos.keys())
        
        id_superior = lista_ids[0]
        tarjeta_superior = crear_tarjeta_estilo(id_superior, config_elementos[id_superior], 75, posicion="centro")

        ids_restantes = lista_ids[1:]
        mitad = math.ceil(len(ids_restantes) / 2)
        ids_izq = ids_restantes[:mitad]
        ids_der = ids_restantes[mitad:]

        tarjetas_izq = [
            crear_tarjeta_estilo(i, config_elementos[i], 70 + (i * 3) % 20, posicion="der") for i in ids_izq
        ]
        
        tarjetas_der = [
            crear_tarjeta_estilo(i, config_elementos[i], 65 + (i * 4) % 25, posicion="izq") for i in ids_der
        ]

        elementos_espaciadores = []
        for idx, row in df.iterrows():
            elementos_espaciadores.append(
                html.Div(style={
                    "width": "34px", "height": "34px", 
                    "marginBottom": "20px"
                })
            )

        espacio_vacio_central = html.Div(
            elementos_espaciadores,
            className="d-flex flex-column align-items-center justify-content-center",
            style={"paddingTop": "0px"}
        )

        panel_areas_central = html.Div(
            id="contenedor-areas-dinamico",
            children=[
                html.Div([
                    html.Div([
                        html.I(className="bi bi-folder-fill text-white me-2", style={"fontSize": "1rem"}),
                        html.H6("ÁREAS ADMINISTRATIVAS", className="text-white fw-bold m-0", style={"fontSize": "0.8rem", "letterSpacing": "0.5px"})
                    ], className="d-flex align-items-center p-3", style={
                        "backgroundColor": "#1ca2a9",
                        "borderTopLeftRadius": "14px",
                        "borderTopRightRadius": "14px",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                    }),
                    html.Div(
                        id="contenedor-botones-areas", 
                        children=[
                            html.Small("Selecciona un acuerdo.", className="text-muted fst-italic p-3", style={"fontSize": "0.75rem"})
                        ], 
                        className="d-flex flex-column gap-1 p-3 position-relative",
                        style={
                            "borderBottomLeftRadius": "14px",
                            "borderBottomRightRadius": "14px",
                            "background": "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%)"
                        }
                    )
                ], className="bg-white mx-auto", style={
                    "borderRadius": "14px", 
                    "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                    "width": "100%", 
                    "maxWidth": "440px",
                    "border": "1px solid rgba(255,255,255,0.8)"
                })
            ],
            style={"display": "none", "width": "100%"}
        )

        layout_distribucion = html.Div([
            dbc.Row([
                dbc.Col(tarjeta_superior, xs=12, md=8, className="mx-auto")
            ], className="mb-2"),
            
            dbc.Row([
                dbc.Col(
                    html.Div(tarjetas_izq, className="d-flex flex-column align-items-center w-100"), 
                    xs=12, md=4
                ),
                dbc.Col([
                    html.Div(espacio_vacio_central, id="wrapper-circulos"),
                    panel_areas_central
                ], xs=12, md=4, className="d-flex flex-column align-items-center justify-content-start pt-0"),
                dbc.Col(
                    html.Div(tarjetas_der, className="d-flex flex-column align-items-center w-100"), 
                    xs=12, md=4
                )
            ], className="align-items-start")
        ], style={
            "backgroundColor": "#e8ecf2", 
            "backgroundImage": "radial-gradient(#cbd5e1 0.75px, transparent 0.75px)",
            "backgroundSize": "16px 16px",
            "minHeight": "auto", 
            "padding": "10px 20px 15px 20px", 
            "borderRadius": "16px"
        })

        return html.Div([layout_distribucion])

    @app.callback(
        [
            Output("contenedor-botones-areas", "children"),
            Output("contenedor-areas-dinamico", "style"),
            Output("wrapper-circulos", "style"),
        ],
        [Input({"type": "btn-acuerdo", "index": ALL}, "n_clicks")],
        prevent_initial_call=True,
    )
    def desplegar_areas(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update

        prop_id = ctx.triggered[0]["prop_id"]
        if "value" in prop_id or not any(x for x in n_clicks if x is not None):
            return no_update, no_update, no_update

        try:
            match_idx = re.search(r'"index":\s*(\d+)', prop_id)
            idx = int(match_idx.group(1)) if match_idx else None
        except Exception:
            return no_update, no_update, no_update

        if idx is None:
            return no_update, no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        df = pd.read_sql_query(
            f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn
        )
        conn.close()

        if df.empty:
            contenido_vacio = html.Small("⚠️ No hay áreas asignadas.", className="text-muted fst-italic", style={"fontSize": "0.75rem"})
            return contenido_vacio, {"display": "block", "width": "100%"}, {"display": "none"}

        def extraer_clave_orden(nombre):
            match = re.match(r"^([\d\.]+)", str(nombre).strip())
            if match:
                partes = match.group(1).split(".")
                return [int(p) for p in partes if p.isdigit()]
            return [999]

        df["orden_num"] = df["nombre"].apply(extraer_clave_orden)
        df = df.sort_values(by="orden_num").drop(columns=["orden_num"])

        elementos_lista = []
        for _, a in df.iterrows():
            nombre_area = a["nombre"]
            match_clave = re.match(r"^([\d\.]+)\s*(.*)", nombre_area)
            if match_clave:
                num_tag = match_clave.group(1)
                texto_tag = match_clave.group(2)
            else:
                num_tag = "•"
                texto_tag = nombre_area

            item_content = html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                num_tag,
                                style={
                                    "backgroundColor": "#1ca2a9",
                                    "color": "#FFFFFF",
                                    "padding": "2px 6px",
                                    "borderRadius": "50%",
                                    "fontSize": "0.65rem",
                                    "fontWeight": "700",
                                    "marginRight": "8px",
                                    "minWidth": "22px",
                                    "height": "22px",
                                    "display": "inline-flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "boxShadow": "0 2px 4px rgba(28, 162, 169, 0.2)",
                                    "flexShrink": "0"
                                },
                            ),
                            html.Span(
                                texto_tag.upper(),
                                style={
                                    "fontSize": "0.68rem",
                                    "fontWeight": "600",
                                    "color": "#1e293b",
                                    "letterSpacing": "0.2px",
                                    "lineHeight": "1.1",
                                    "whiteSpace": "normal",
                                    "wordBreak": "break-word"
                                },
                            ),
                        ],
                        className="d-flex align-items-center position-relative w-100",
                        style={"zIndex": "2"}
                    )
                ],
                className="d-flex align-items-center justify-content-between w-100"
            )

            elementos_lista.append(
                dbc.Button(
                    item_content,
                    id={"type": "btn-area", "index": a["id"]},
                    color="light",
                    className="shadow-sm border mb-1 text-start w-100 py-1 px-2 position-relative",
                    style={
                        "borderRadius": "8px",
                        "backgroundColor": "#f8fafc",
                        "borderColor": "#e2e8f0",
                        "transition": "all 0.2s ease"
                    },
                )
            )

        lista_con_linea = html.Div(
            [
                html.Div(style={
                    "position": "absolute",
                    "left": "22px",
                    "top": "12px",
                    "bottom": "12px",
                    "width": "2px",
                    "backgroundColor": "#1ca2a9",
                    "zIndex": "1"
                }),
                html.Div(elementos_lista, className="d-flex flex-column gap-1 position-relative", style={"zIndex": "2"})
            ],
            className="position-relative py-1",
            style={
                "maxHeight": "320px", 
                "overflowY": "auto", 
                "overflowX": "hidden",
                "paddingRight": "4px"
            }
        )

        return lista_con_linea, {"display": "block", "width": "100%"}, {"display": "none"}

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
                        style={"fontSize": "0.95rem", "color": "#781d37"},
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
                    "borderLeft": "5px solid #781d37",
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
                            "color": "#781d37",
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
                            style={"fontSize": "1.1rem", "fontWeight": "700", "color": "#781d37"},
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

    @app.callback(
        Output("download-excel-mir-original", "data"),
        Input("btn-descargar-mir-original", "n_clicks"),
        prevent_initial_call=True,
    )
    def descargar_matriz_mir_original(n_clicks):
        if not n_clicks:
            return no_update

        nombre_archivo = "DES01_CHU_02_2026.xlsx"

        rutas_posibles = [
            nombre_archivo,
            os.path.join("uploads", nombre_archivo),
            os.path.join("data", nombre_archivo)
        ]
        
        for ruta in rutas_posibles:
            if os.path.exists(ruta):
                return dcc.send_file(ruta)

        file_id = "11jBjOTf6nqwGzaVMj4AQyR4ApYT2MaYJ"
        url_descarga_drive = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

        try:
            req = urllib.request.Request(url_descarga_drive, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                contenido_archivo = response.read()
            
            return dict(content=contenido_archivo, filename=nombre_archivo)
        except Exception as e:
            df_error = pd.DataFrame({"Error": [f"No se pudo descargar el archivo original '{nombre_archivo}': {str(e)}"]})
            return dcc.send_data_frame(df_error.to_excel, "Error_Descarga.xlsx", index=False)