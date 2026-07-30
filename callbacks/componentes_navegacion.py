import math
import re
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import pandas as pd

TAMANO_PAGINA = 10

DICCIONARIO_AREAS = {
    "5_1_1_RECEPCION_MUNICIPAL_PRESIDENTA": {
        "resumen": (
            "Registro y control de las solicitudes ciudadanas, apoyos económicos"
            " y gestiones institucionales atendidas en la oficina de la"
            " Presidencia Municipal."
        ),
        "objetivo": (
            "Garantizar una atención ciudadana oportuna, transparente y de"
            " alto impacto social directa en las comunidades."
        ),
    }
}

DICCIONARIO_ICONOS_ACUERDOS = {
    1: "bi bi-handshake",
    2: "bi bi-heart-pulse",
    3: "bi bi-cash-coin",
    4: "bi bi-lightbulb",
}


def extraer_clave_area(cadena_area):
    if not cadena_area or pd.isnull(cadena_area):
        return ""
    cadena_str = str(cadena_area).strip()
    match = re.match(r"^(\d+[\._\d]+)", cadena_str)
    if match:
        return match.group(1).replace("_", ".")
    return cadena_str.upper()


def filtrar_df_mir_por_area_exacta(df_mir, area_seleccionada):
    if df_mir.empty or not area_seleccionada:
        return df_mir

    col_area = None
    for col in df_mir.columns:
        if str(col).lower() in ["area", "área", "clave_area", "id_area", "nombre_area", "eje_area"]:
            col_area = col
            break

    if not col_area:
        return df_mir

    clave_buscada = extraer_clave_area(area_seleccionada)

    def coincide_exactamente(val_celda):
        if pd.isnull(val_celda):
            return False
        clave_celda = extraer_clave_area(val_celda)
        if clave_celda:
            return clave_celda == clave_buscada
        val_norm = str(val_celda).strip().upper().replace("_", ".")
        area_norm = str(area_seleccionada).strip().upper().replace("_", ".")
        return val_norm == area_norm

    mascara = df_mir[col_area].apply(coincide_exactamente)
    return df_mir[mascara]


def diseñar_tarjeta_pbr(datos_pbr):
    if not datos_pbr:
        return html.Div()
    if isinstance(datos_pbr, list):
        return dbc.Row(datos_pbr, className="mb-4")
    if isinstance(datos_pbr, dict):
        color_map = {
            "Verde": "success",
            "Amarillo": "warning",
            "Rojo": "danger",
            "Azul": "info",
        }
        color_alerta = color_map.get(datos_pbr.get("estatus_semaforo"), "light")
        return dbc.Alert(
            [
                html.H5(
                    "🎯 EVALUACIÓN DE DESEMPEÑO INSTITUCIONAL (PbR)",
                    className="alert-heading pbr-titulo",
                ),
                html.Hr(className="pbr-linea"),
                dbc.Row([
                    dbc.Col(
                        [
                            html.P(
                                f"📊 Cumplimiento: {datos_pbr.get('porcentaje_cumplimiento', 0)}%",
                                className="pbr-texto-destacado",
                            ),
                            html.P(
                                f"📋 Metas Programadas: {datos_pbr.get('total_metas_programadas', 0)}",
                                className="pbr-texto-secundario",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.P(
                                f"✅ Metas Alcanzadas: {datos_pbr.get('total_metas_alcanzadas', 0)}",
                                className="pbr-texto-destacado",
                            ),
                            html.P(
                                f"💬 Estatus: {datos_pbr.get('mensaje', '')}",
                                className="pbr-texto-secundario",
                            ),
                        ],
                        md=6,
                    ),
                ]),
            ],
            color=color_alerta,
            className="pbr-alerta-contenedor",
        )
    return datos_pbr


def construir_tabla_estilo_cards(df, pagina_actual=1):
    if df.empty:
        return html.Div(
            "No hay datos registrados en esta área.",
            className="text-center text-muted p-4 fw-bold",
        )

    total_registros = len(df)
    total_paginas = math.ceil(total_registros / TAMANO_PAGINA) if total_registros > 0 else 1
    pagina_actual = max(1, min(pagina_actual, total_paginas))

    inicio = (pagina_actual - 1) * TAMANO_PAGINA
    fin = inicio + TAMANO_PAGINA
    df_pagina = df.iloc[inicio:fin]

    clases_colores = ["bg-col-1", "bg-col-2", "bg-col-3", "bg-col-4", "bg-col-5", "bg-col-6"]
    cols_a_mostrar = [c for c in df.columns if str(c).lower() not in ["rowid", "id"]]
    columnas_tarjetas = []

    for idx, col_name in enumerate(cols_a_mostrar):
        clase_color = clases_colores[idx % len(clases_colores)]
        valores = df_pagina[col_name].tolist()

        filas_celda = []
        for i, val in enumerate(valores):
            clase_bg = "bg-celda-par" if i % 2 == 0 else "bg-celda-impar"
            val_str = str(val) if pd.notnull(val) else "-"
            if isinstance(val, (int, float)) and "inversión" in str(col_name).lower():
                val_str = f"${val:,.2f}"

            filas_celda.append(
                html.Div(val_str, className=f"celda-card-registro {clase_bg}")
            )

        tarjeta_columna = html.Div(
            [
                html.Div(
                    html.H6(str(col_name).replace("_", " ").upper()),
                    className=f"header-card-columna {clase_color}",
                ),
                html.Div(filas_celda, className="cuerpo-card-columna"),
                html.Div(
                    html.Span("REGISTRO"),
                    className=f"footer-card-columna {clase_color}",
                ),
            ],
            className="columna-card-registro",
        )
        columnas_tarjetas.append(tarjeta_columna)

    vista_tarjetas = html.Div(columnas_tarjetas, className="contenedor-cards-scroll")

    barra_paginacion = html.Div(
        [
            html.Div(
                [
                    html.Span("Mostrando registros ", className="text-muted small"),
                    html.Span(f"{inicio + 1} - {min(fin, total_registros)}", className="fw-bold text-dark small"),
                    html.Span(f" de {total_registros}", className="text-muted small"),
                ],
                className="d-none d-sm-block",
            ),
            html.Div(
                [
                    dbc.Button("«", id="btn-pag-inicio", color="light", size="sm", className="me-1 border", disabled=(pagina_actual == 1)),
                    dbc.Button("‹", id="btn-pag-prev", color="light", size="sm", className="me-2 border", disabled=(pagina_actual == 1)),
                    dbc.Badge(f"Página {pagina_actual} de {total_paginas}", color="white", text_color="dark", className="border px-3 py-2 fw-bold shadow-sm small"),
                    dbc.Button("›", id="btn-pag-next", color="light", size="sm", className="ms-2 border", disabled=(pagina_actual >= total_paginas)),
                    dbc.Button("»", id="btn-pag-fin", color="light", size="sm", className="ms-1 border", disabled=(pagina_actual >= total_paginas)),
                ],
                className="d-flex align-items-center",
            ),
        ],
        className="barra-paginacion-contenedor",
    )

    return html.Div([vista_tarjetas, barra_paginacion])


def diseñar_tabla_mir_consolidada(df_mir, area_seleccionada=None):
    if area_seleccionada:
        df_mir = filtrar_df_mir_por_area_exacta(df_mir, area_seleccionada)

    if df_mir.empty:
        return html.Div(
            "No hay registros disponibles en la Matriz MIR para esta área específica.",
            className="text-center text-muted p-4 fw-bold",
        )

    cols_a_mostrar = [c for c in df_mir.columns if str(c).lower() not in ["rowid", "id", "area", "área", "clave_area"]]

    header_nivel_1 = html.Tr([
        html.Th("INFORMACIÓN DEL PROGRAMA", colSpan=5, className="th-mir-grupo th-mir-border-right", style={"backgroundColor": "#1ca2a9 !important", "color": "#FFFFFF !important", "fontWeight": "800 !important"}),
        html.Th("DATOS DEL INDICADOR Y METAS", colSpan=max(1, len(cols_a_mostrar) - 5), className="th-mir-grupo", style={"backgroundColor": "#1ca2a9 !important", "color": "#FFFFFF !important", "fontWeight": "800 !important"}),
    ])

    def renombrar_porcentajes_trimestrales(columnas):
        nombres_trimestres = ["PRIMER TRIMESTRE", "SEGUNDO TRIMESTRE", "TERCER TRIMESTRE", "CUARTO TRIMESTRE"]
        contador_trimestre = 0
        nuevas_cols = []
        for col in columnas:
            nombre = str(col).replace("_", " ").upper().strip()
            if any(k in nombre for k in ["SEMÁFORO.4", "SEMAFORO.4", "SEMAFORO 4"]):
                nuevas_cols.append("SEMÁFORO DE CUMPLIMIENTO ANUAL")
            elif "PORCENTAJE ALCANZADO" in nombre:
                if contador_trimestre < len(nombres_trimestres):
                    nuevas_cols.append(nombres_trimestres[contador_trimestre])
                    contador_trimestre += 1
                else:
                    nuevas_cols.append(nombre)
            else:
                nuevas_cols.append(nombre)
        return nuevas_cols

    headers_nivel_2_nombres = renombrar_porcentajes_trimestrales(cols_a_mostrar)
    headers_nivel_2 = [
        html.Th(nombre_col, className="th-mir-columna", style={"backgroundColor": "#920d24 !important", "color": "#FFFFFF !important", "fontWeight": "800 !important"}) 
        for nombre_col in headers_nivel_2_nombres
    ]
    header_nivel_2 = html.Tr(headers_nivel_2)

    filas_construidas = []
    for idx_row, row in df_mir.iterrows():
        bg_fila = "bg-celda-par" if idx_row % 2 == 0 else "bg-celda-impar"
        celdas = []

        for idx_col, col in enumerate(cols_a_mostrar):
            val = row[col]
            col_nombre = str(col).upper()

            if pd.isnull(val) or str(val).strip() in ["", "nan", "None"]:
                contenido_celda = "-"
            elif "NIVEL" in col_nombre:
                nivel_key = str(val).strip().upper()
                clase_badge = {
                    "FIN": "badge-fin",
                    "PROPÓSITO": "badge-proposito",
                    "COMPONENTE": "badge-componente",
                    "ACTIVIDAD": "badge-actividad",
                }.get(nivel_key, "badge-default")
                contenido_celda = html.Span(nivel_key, className=f"badge-nivel {clase_badge}")
            elif isinstance(val, (int, float)):
                if (
                    "PORCENTAJE" in col_nombre
                    or "TRIMESTRE" in headers_nivel_2_nombres[idx_col]
                    or (isinstance(val, float) and 0 < val <= 1.0)
                ):
                    contenido_celda = f"{round(val * 100)}%"
                else:
                    contenido_celda = f"{val:g}"
            else:
                contenido_celda = str(val)

            es_centrado = (
                any(k in col_nombre for k in ["NIVEL", "EJE", "CLAVE", "SEMÁFORO", "SEMAFORO", "TRIMESTRE"])
                or "PORCENTAJE" in col_nombre
            )
            celdas.append(html.Td(contenido_celda, className=f"td-mir-celda {'text-center' if es_centrado else 'text-start'}"))

        filas_construidas.append(html.Tr(celdas, className=bg_fila))

    fila_principal = filas_construidas[0] if filas_construidas else None
    filas_adicionales = filas_construidas[1:] if len(filas_construidas) > 1 else []

    # 🟢 SECCIÓN INSTITUCIONAL CENTRADA CON BORDES SIMÉTRICOS EN #1ca2a9 (Corregido)
    seccion_titulo_institucional = html.Div(
        [
            html.I(className="bi bi-bar-chart-fill me-2", style={"color": "#1ca2a9", "fontSize": "1.1rem"}),
            html.Span(
                "MATRIZ DE INDICADORES ESPECIFICOS RELACIONADOS AL ÁREA",
                style={
                    "color": "#781d37",
                    "fontWeight": "bold",
                    "fontSize": "0.95rem",
                    "letterSpacing": "0.5px"
                }
            )
        ],
        className="p-3 mb-3 bg-white rounded-3 shadow-sm d-flex align-items-center justify-content-center",
        style={
            "borderLeft": "4px solid #1ca2a9",
            "borderRight": "4px solid #1ca2a9"
        }
    )

    encabezado_mir = html.Div(
        [
            html.I(className="bi bi-clipboard-data-fill me-2 mir-icono-titulo"),
            html.Span("MATRIZ DE INDICADORES ESPECIFICOS", className="mir-titulo-principal"),
            html.Span(" — Vista Especifica", className="mir-subtitulo"),
        ],
        className="mb-2 d-flex align-items-center px-1",
    )

    tbody_elementos = []
    if fila_principal:
        tbody_elementos.append(fila_principal)

    if filas_adicionales:
        tbody_elementos.append(
            dbc.Collapse(
                filas_adicionales,
                id="collapse-mir-extra-py",
                is_open=False,
            )
        )

    tabla_unificada_html = html.Table(
        [html.Thead([header_nivel_1, header_nivel_2]), html.Tbody(tbody_elementos)],
        className="tabla-mir-custom",
    )

    boton_desplegar = html.Div()
    if filas_adicionales:
        boton_desplegar = dbc.Button(
            f"👇 MOSTRAR OTROS {len(filas_adicionales)} INDICADORES DEL ÁREA",
            id="btn-toggle-mir-extra-py",
            color="light",
            size="sm",
            className="btn-toggle-mir-extra",
        )

    contenedor_mir = html.Div(
        [
            html.Div(tabla_unificada_html, className="table-responsive"),
            boton_desplegar,
        ],
        className="tabla-mir-contenedor",
    )

    return html.Div([seccion_titulo_institucional, encabezado_mir, contenedor_mir])


@callback(
    [
        Output("collapse-mir-extra-py", "is_open"),
        Output("btn-toggle-mir-extra-py", "children"),
    ],
    [Input("btn-toggle-mir-extra-py", "n_clicks")],
    [
        State("collapse-mir-extra-py", "is_open"),
        State("btn-toggle-mir-extra-py", "children"),
    ],
    prevent_initial_call=True,
)
def alternar_filas_mir_python(n_clicks, is_open, texto_actual):
    if not n_clicks:
        return is_open, texto_actual

    nuevo_estado = not is_open

    if nuevo_estado:
        texto = "👆 OCULTAR INDICADORES ADICIONALES"
    else:
        if "INDICADORES DEL ÁREA" in str(texto_actual):
            texto = str(texto_actual).replace("👆 OCULTAR INDICADORES ADICIONALES", "").strip()
            if not texto:
                texto = "👇 MOSTRAR OTROS INDICADORES DEL ÁREA"
        else:
            texto = "👇 MOSTRAR OTROS INDICADORES DEL ÁREA"

    return nuevo_estado, texto