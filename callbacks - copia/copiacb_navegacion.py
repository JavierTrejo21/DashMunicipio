import sqlite3
import json
import math
import re
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, ALL, dash_table, no_update
import dash_bootstrap_components as dbc

from database import normalizar_nombre_tabla, DB_GESTION
from visualizaciones import generar_tablero_impacto, seccion_impacto_layout
from indicadores_pbr import calcular_indicadores_pbr

TAMANO_PAGINA = 10  # Registros máximos por página para tablas operativas

DICCIONARIO_AREAS = {
    "5_1_1_RECEPCION_MUNICIPAL_PRESIDENTA": {
        "resumen": "Registro y control de las solicitudes ciudadanas, apoyos económicos y gestiones institucionales atendidas en la oficina de la Presidencia Municipal.",
        "objetivo": "Garantizar una atención ciudadana oportuna, transparente y de alto impacto social directa en las comunidades."
    }
}

DICCIONARIO_ICONOS_ACUERDOS = {
    1: "bi bi-handshake", 
    2: "bi bi-heart-pulse", 
    3: "bi bi-cash-coin", 
    4: "bi bi-lightbulb"
}

# ------------------------------------------------------------------------------
# 1. DISEÑO DE EVALUACIÓN PbR
# ------------------------------------------------------------------------------
def diseñar_tarjeta_pbr(datos_pbr):
    if not datos_pbr:
        return dbc.Alert("Esperando integración de datos...", color="light")
    if isinstance(datos_pbr, list):
        return dbc.Row(datos_pbr, className="mb-4")
    if isinstance(datos_pbr, dict):
        color_map = {"Verde": "success", "Amarillo": "warning", "Rojo": "danger", "Azul": "info"}
        color_alerta = color_map.get(datos_pbr.get('estatus_semaforo'), "light")
        return dbc.Alert([
            html.H5("🎯 EVALUACIÓN DE DESEMPEÑO INSTITUCIONAL (PbR)", className="alert-heading font-weight-bold", style={"fontSize": "0.85rem"}),
            html.Hr(style={"margin": "6px 0"}),
            dbc.Row([
                dbc.Col([
                    html.P(f"📊 Cumplimiento: {datos_pbr.get('porcentaje_cumplimiento', 0)}%", className="mb-1 font-weight-bold", style={"fontSize": "0.8rem"}),
                    html.P(f"📋 Metas Programadas: {datos_pbr.get('total_metas_programadas', 0)}", className="mb-0 text-muted", style={"fontSize": "0.72rem"})
                ], md=6),
                dbc.Col([
                    html.P(f"✅ Metas Alcanzadas: {datos_pbr.get('total_metas_alcanzadas', 0)}", className="mb-1 font-weight-bold", style={"fontSize": "0.8rem"}),
                    html.P(f"💬 Estatus: {datos_pbr.get('mensaje', '')}", className="mb-0 text-muted", style={"fontSize": "0.72rem"})
                ], md=6)
            ])
        ], color=color_alerta, className="shadow-sm border-0 mb-3")
    
    return datos_pbr


# ------------------------------------------------------------------------------
# 2. TABLA OPERATIVA ESTILO TARJETAS VERTICALES (PAGINADA)
# ------------------------------------------------------------------------------
def construir_tabla_estilo_cards(df, pagina_actual=1):
    if df.empty:
        return html.Div("No hay datos registrados en esta área.", className="text-center text-muted p-3")

    total_registros = len(df)
    total_paginas = math.ceil(total_registros / TAMANO_PAGINA) if total_registros > 0 else 1
    pagina_actual = max(1, min(pagina_actual, total_paginas))

    inicio = (pagina_actual - 1) * TAMANO_PAGINA
    fin = inicio + TAMANO_PAGINA
    df_pagina = df.iloc[inicio:fin]

    paleta_headers = [
        {"bg": "#0D9488", "text": "#FFFFFF"},
        {"bg": "#691C32", "text": "#FFFFFF"},
        {"bg": "#0F766E", "text": "#FFFFFF"},
        {"bg": "#4A1525", "text": "#FFFFFF"},
        {"bg": "#14B8A6", "text": "#FFFFFF"},
        {"bg": "#85223D", "text": "#FFFFFF"},
    ]

    cols_a_mostrar = [c for c in df.columns if c.lower() not in ['rowid', 'id']]
    columnas_tarjetas = []

    for idx, col_name in enumerate(cols_a_mostrar):
        color_estilo = paleta_headers[idx % len(paleta_headers)]
        valores = df_pagina[col_name].tolist()
        
        filas_celda = []
        for i, val in enumerate(valores):
            bg_fila = "#F8FAFC" if i % 2 == 0 else "#FFFFFF"
            val_str = str(val) if pd.notnull(val) else "-"
            if isinstance(val, (int, float)) and "inversión" in col_name.lower():
                val_str = f"${val:,.2f}"

            filas_celda.append(
                html.Div(
                    val_str,
                    style={
                        "padding": "6px 6px",
                        "backgroundColor": bg_fila,
                        "fontSize": "0.75rem",
                        "color": "#334155",
                        "borderBottom": "1px solid #F1F5F9",
                        "textAlign": "center",
                        "fontWeight": "500",
                        "minHeight": "32px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "wordBreak": "break-word",
                        "lineHeight": "1.2"
                    }
                )
            )

        tarjeta_columna = html.Div([
            html.Div([
                html.H6(
                    col_name.replace('_', ' ').upper(),
                    style={"margin": "0", "fontSize": "0.75rem", "fontWeight": "700", "letterSpacing": "0.5px"}
                )
            ], style={
                "backgroundColor": color_estilo["bg"],
                "color": color_estilo["text"],
                "padding": "8px 6px",
                "borderTopLeftRadius": "12px",
                "borderTopRightRadius": "12px",
                "textAlign": "center",
                "boxShadow": "inset 0 -1px 3px rgba(0,0,0,0.12)"
            }),
            
            html.Div(filas_celda, style={"flex": "1"}),
            
            html.Div(
                html.Span("REGISTRO", style={"fontSize": "0.62rem", "fontWeight": "700", "letterSpacing": "0.8px"}),
                style={
                    "backgroundColor": color_estilo["bg"],
                    "color": color_estilo["text"],
                    "padding": "4px 6px",
                    "borderBottomLeftRadius": "12px",
                    "borderBottomRightRadius": "12px",
                    "textAlign": "center",
                    "opacity": "0.95"
                }
            )
        ], style={
            "flex": "1 1 140px",
            "minWidth": "130px",
            "maxWidth": "200px",
            "borderRadius": "12px",
            "backgroundColor": "#FFFFFF",
            "boxShadow": "0 4px 6px -1px rgba(0,0,0,0.05)",
            "border": "1px solid #E2E8F0",
            "display": "flex",
            "flexDirection": "column",
            "overflow": "hidden"
        })

        columnas_tarjetas.append(tarjeta_columna)

    vista_tarjetas = html.Div(
        columnas_tarjetas,
        style={
            "display": "flex",
            "gap": "8px",
            "overflowX": "auto",
            "padding": "5px 2px 10px 2px",
            "alignItems": "stretch"
        }
    )

    barra_paginacion = html.Div([
        html.Div([
            html.Span("Mostrando registros ", className="text-muted", style={"fontSize": "0.78rem"}),
            html.Span(f"{inicio + 1} - {min(fin, total_registros)}", className="fw-bold text-dark", style={"fontSize": "0.78rem"}),
            html.Span(f" de {total_registros}", className="text-muted", style={"fontSize": "0.78rem"})
        ], className="d-none d-sm-block"),

        html.Div([
            dbc.Button("«", id="btn-pag-inicio", color="light", size="sm", className="me-1 border", disabled=(pagina_actual == 1)),
            dbc.Button("‹", id="btn-pag-prev", color="light", size="sm", className="me-2 border", disabled=(pagina_actual == 1)),
            
            dbc.Badge(
                f"Página {pagina_actual} de {total_paginas}",
                color="white",
                text_color="dark",
                className="border px-3 py-2 fw-bold shadow-sm",
                style={"fontSize": "0.8rem", "borderColor": "#CBD5E1"}
            ),
            
            dbc.Button("›", id="btn-pag-next", color="light", size="sm", className="ms-2 border", disabled=(pagina_actual >= total_paginas)),
            dbc.Button("»", id="btn-pag-fin", color="light", size="sm", className="ms-1 border", disabled=(pagina_actual >= total_paginas)),
        ], className="d-flex align-items-center")
    ], className="d-flex justify-content-between align-items-center mt-3 px-2 py-2 bg-light rounded-3 border")

    return html.Div([
        vista_tarjetas,
        barra_paginacion
    ])


# ------------------------------------------------------------------------------
# 3. DISEÑO EJECUTIVO PARA LA MATRIZ MIR CONSOLIDADA (ALTA DIRECCIÓN)
# ------------------------------------------------------------------------------
def diseñar_tabla_mir_consolidada(df_mir):
    if df_mir.empty:
        return html.Div("No hay registros disponibles en la Matriz MIR.", className="text-center text-muted p-4")

    ESTILO_NIVEL = {
        "FIN": {"bg": "#0D9488", "color": "#FFFFFF"},          # Turquesa destacado
        "PROPÓSITO": {"bg": "#691C32", "color": "#FFFFFF"},    # Guinda
        "COMPONENTE": {"bg": "#334155", "color": "#FFFFFF"},   # Gris Pizarra
        "ACTIVIDAD": {"bg": "#E2E8F0", "color": "#1E293B"}     # Gris Claro
    }

    cols_a_mostrar = [c for c in df_mir.columns if c.lower() not in ['rowid', 'id']]

    headers = [
        html.Th(
            col.replace('_', ' ').upper(),
            style={
                "backgroundColor": "#0D9488",
                "color": "#FFFFFF",
                "padding": "12px 10px",
                "fontSize": "0.72rem",
                "fontWeight": "700",
                "letterSpacing": "0.6px",
                "border": "none",
                "textAlign": "center",
                "whiteSpace": "nowrap",
                "verticalAlign": "middle"
            }
        ) for col in cols_a_mostrar
    ]

    filas_tabla = []
    for idx_row, row in df_mir.iterrows():
        bg_fila = "#F8FAFC" if idx_row % 2 == 0 else "#FFFFFF"
        celdas = []
        
        for col in cols_a_mostrar:
            val = row[col]
            val_str = str(val) if pd.notnull(val) else "-"
            
            if col.upper() == "NIVEL":
                nivel_key = str(val).strip().upper()
                estilo_badge = ESTILO_NIVEL.get(nivel_key, {"bg": "#CBD5E1", "color": "#0F172A"})
                
                contenido_celda = html.Span(
                    nivel_key,
                    style={
                        "backgroundColor": estilo_badge["bg"],
                        "color": estilo_badge["color"],
                        "padding": "4px 10px",
                        "borderRadius": "12px",
                        "fontSize": "0.68rem",
                        "fontWeight": "700",
                        "letterSpacing": "0.5px",
                        "display": "inline-block"
                    }
                )
            else:
                contenido_celda = val_str

            celdas.append(
                html.Td(
                    contenido_celda,
                    style={
                        "padding": "10px 12px",
                        "fontSize": "0.76rem",
                        "color": "#1E293B",
                        "fontWeight": "500",
                        "textAlign": "center" if col.upper() in ["NIVEL", "EJE O ACUERDO DEL PMD"] else "left",
                        "borderBottom": "1px solid #E2E8F0",
                        "verticalAlign": "middle",
                        "lineHeight": "1.3"
                    }
                )
            )

        filas_tabla.append(
            html.Tr(
                celdas, 
                style={"backgroundColor": bg_fila}
            )
        )

    boton_ver_general = dbc.Button(
        [
            html.I(className="bi bi-bar-chart-line-fill me-2", style={"fontSize": "1rem", "color": "#0D9488"}),
            html.Span("VER MATRIZ MIR GENERAL (ALTA DIRECCIÓN)", style={"fontWeight": "700", "letterSpacing": "0.5px", "fontSize": "0.8rem"})
        ],
        id="btn-ver-mir-general",
        color="light",
        className="w-100 mb-3 shadow-sm border d-flex align-items-center justify-content-center py-2",
        style={
            "borderRadius": "12px",
            "borderColor": "#CBD5E1",
            "backgroundColor": "#FFFFFF",
            "color": "#1E293B"
        }
    )

    encabezado_mir = html.Div([
        html.I(className="bi bi-file-earmark-spreadsheet-fill me-2", style={"color": "#0D9488", "fontSize": "1.1rem"}),
        html.Span("MATRIZ DE INDICADORES PARA RESULTADOS (MIR CONSOLIDADA)", style={"fontWeight": "800", "color": "#0D9488", "fontSize": "0.85rem", "letterSpacing": "0.4px"}),
        html.Span(" — VISTA EJECUTIVA CONSOLIDADA", style={"color": "#64748B", "fontSize": "0.75rem", "fontWeight": "600"})
    ], className="mb-2 d-flex align-items-center px-1")

    tabla_html = html.Table(
        [html.Thead(html.Tr(headers)), html.Tbody(filas_tabla)],
        style={"width": "100%", "borderCollapse": "collapse", "margin": "0"}
    )

    contenedor_mir = html.Div([
        html.Div(tabla_html, style={"overflowX": "auto", "width": "100%"})
    ], style={
        "borderRadius": "14px",
        "backgroundColor": "#FFFFFF",
        "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.05)",
        "border": "1px solid #E2E8F0",
        "borderTop": "4px solid #0D9488",
        "overflow": "hidden",
        "marginBottom": "20px"
    })

    return html.Div([
        boton_ver_general,
        encabezado_mir,
        contenedor_mir
    ])


# ------------------------------------------------------------------------------
# 4. REGISTRO DE CALLBACKS
# ------------------------------------------------------------------------------
def register_navegacion_callbacks(app):
    
    @app.callback(
        Output('contenedor-tarjetas-acuerdos', 'children'),
        Input('contenedor-tarjetas-acuerdos', 'id')
    )
    def cargar_acuerdos(_):
        conn = sqlite3.connect(DB_GESTION)
        try:
            df = pd.read_sql_query("SELECT * FROM acuerdos", conn)
        except:
            df = pd.DataFrame()
            
        if df.empty:
            ejes_defecto = [
                (1, "GOBIERNO PARTICIPATIVO Y TRANSFORMADOR"),
                (2, "BIENESTAR Y PROSPERIDAD"),
                (3, "DESARROLLO ECONÓMICO Y CULTURAL"),
                (4, "DESARROLLO SOSTENIBLE E INFRAESTRUCTURA")
            ]
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS acuerdos (id INTEGER PRIMARY KEY, nombre TEXT)")
            cursor.executemany("INSERT OR IGNORE INTO acuerdos (id, nombre) VALUES (?, ?)", ejes_defecto)
            conn.commit()
            df = pd.read_sql_query("SELECT * FROM acuerdos", conn)
            
        conn.close()
        
        tarjetas = []
        for _, f in df.iterrows():
            id_acuerdo = int(f['id'])
            nombre_acuerdo = f['nombre']
            porcentaje_base = 85 if id_acuerdo == 1 else (70 if id_acuerdo == 2 else (90 if id_acuerdo == 3 else 60))
            icono_clase = DICCIONARIO_ICONOS_ACUERDOS.get(id_acuerdo, "bi bi-folder")
            
            fig_dona = go.Figure(go.Pie(values=[porcentaje_base, 100 - porcentaje_base], hole=0.72, marker_colors=["#691c32", "#e5e7eb"], textinfo='none', hoverinfo='none'))
            fig_dona.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), width=75, height=75, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            
            tarjetas.append(dbc.Col(html.Div([
                html.Div([
                    html.I(className=icono_clase, style={"position": "absolute", "fontSize": "1.3rem", "color": "#691c32", "zIndex": "10"}),
                    dcc.Graph(figure=fig_dona, config={'displayModeBar': False})
                ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "position": "relative", "marginBottom": "15px"}),
                html.P(nombre_acuerdo, className="text-center mb-2 font-weight-bold", style={"fontSize": "0.78rem", "color": "#1f2937", "lineHeight": "1.4"}),
                html.H6(f"{porcentaje_base}%", className="text-center font-weight-bold", style={"color": "#691c32", "fontSize": "0.9rem", "margin": "0"}),
                dbc.Button("", id={'type': 'btn-acuerdo', 'index': id_acuerdo}, style={"position": "absolute", "top": "0", "left": "0", "width": "100%", "height": "100%", "opacity": "0", "cursor": "pointer", "zIndex": "20"})
            ], className="p-4 bg-white border text-center position-relative h-100 shadow-sm", style={"borderRadius": "18px", "borderColor": "#e5e7eb"}), width=12, sm=6, md=3, className="mb-4"))
        return tarjetas

    @app.callback(
        [Output('collapse-areas', 'is_open'), Output('contenedor-botones-areas', 'children')],
        [Input({'type': 'btn-acuerdo', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def desplegar_areas(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update
        
        prop_id = ctx.triggered[0]['prop_id']
        if 'value' in prop_id or not any(x for x in n_clicks if x is not None):
            return no_update, no_update

        try:
            idx = json.loads(prop_id.split('.')[0])['index']
        except (json.JSONDecodeError, KeyError, IndexError):
            return no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        df = pd.read_sql_query(f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn)
        conn.close()
        
        if df.empty:
            return True, html.Small("⚠️ No hay áreas asignadas a este eje estratégico todavía.", className="text-muted p-2")

        def extraer_clave_orden(nombre):
            match = re.match(r"^([\d\.]+)", str(nombre).strip())
            if match:
                partes = match.group(1).split('.')
                return [int(p) for p in partes if p.isdigit()]
            return [999]

        df['orden_num'] = df['nombre'].apply(extraer_clave_orden)
        df = df.sort_values(by='orden_num').drop(columns=['orden_num'])

        botones = []
        for _, a in df.iterrows():
            nombre_area = a['nombre']
            match_clave = re.match(r"^([\d\.]+)\s*(.*)", nombre_area)
            if match_clave:
                num_tag = match_clave.group(1)
                texto_tag = match_clave.group(2)
            else:
                num_tag = "•"
                texto_tag = nombre_area

            btn_content = html.Div([
                html.Span(
                    num_tag,
                    style={
                        "backgroundColor": "#691C32",
                        "color": "#FFFFFF",
                        "padding": "3px 8px",
                        "borderRadius": "8px",
                        "fontSize": "0.72rem",
                        "fontWeight": "700",
                        "marginRight": "8px"
                    }
                ),
                html.Span(
                    texto_tag.upper(),
                    style={
                        "fontSize": "0.75rem",
                        "fontWeight": "600",
                        "color": "#334155",
                        "letterSpacing": "0.3px"
                    }
                )
            ], className="d-flex align-items-center")

            botones.append(
                dbc.Button(
                    btn_content,
                    id={'type': 'btn-area', 'index': a['id']},
                    color="light",
                    className="m-1 shadow-sm border",
                    style={
                        "borderRadius": "10px",
                        "border": "1px solid #CBD5E1",
                        "backgroundColor": "#FFFFFF",
                        "padding": "6px 14px"
                    }
                )
            )

        return True, html.Div(botones, style={"display": "flex", "flexWrap": "wrap", "gap": "6px", "padding": "6px 0"})

    # --- CALLBACK PRINCIPAL CON RENDERIZADO DIRECTO ---
    @app.callback(
        [Output('contenido-area', 'children'), Output('active-info', 'data'), Output('resumen-kpis', 'children')],
        [Input({'type': 'btn-area', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def mostrar_dashboard(n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered or not any(x for x in n_clicks if x is not None): 
            return no_update, no_update, no_update
            
        try:
            prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
            idx = json.loads(prop_id)['index']
        except Exception:
            return no_update, no_update, no_update

        conn = sqlite3.connect(DB_GESTION)
        area_data = pd.read_sql_query("SELECT nombre FROM areas WHERE id=?", conn, params=(idx,))
        
        if area_data.empty: 
            conn.close()
            return dbc.Alert("Área no registrada en la base de datos.", color="warning"), no_update, ""
            
        nombre_area = area_data.iloc[0]['nombre']
        tabla = normalizar_nombre_tabla(nombre_area)
        
        info_est = DICCIONARIO_AREAS.get(tabla, {
            "resumen": "Área operativa integrada en los acuerdos del Plan Municipal.",
            "objetivo": "Seguimiento y evaluación continua de los indicadores sectoriales."
        })
        
        tablas_existentes = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
        
        if tabla not in tablas_existentes:
            conn.close()
            aviso = dbc.Alert([
                html.H5("⚠️ Tabla vacía o no sincronizada", className="alert-heading"),
                html.P(f"El área '{nombre_area}' está registrada pero aún no contiene datos importados en la tabla SQLite '{tabla}'."),
                html.Hr(),
                html.Small("Utiliza el botón de administración en el encabezado para cargar el Excel correspondiente.")
            ], color="warning")
            return aviso, {'tabla': tabla, 'id': idx}, ""

        try:
            df = pd.read_sql_query(f'SELECT rowid, * FROM "{tabla}"', conn)
            conn.close()
            
            datos_pbr_raw = calcular_indicadores_pbr(df)
            resumen_cards = diseñar_tarjeta_pbr(datos_pbr_raw)

            bloque_resumen = dbc.Alert([
                html.H5(f"📌 RESUMEN ESTRATÉGICO: {nombre_area}", className="alert-heading font-weight-bold", style={"fontSize": "0.9rem"}),
                html.P(info_est['resumen'], className="mb-1", style={"fontSize": "0.8rem"}),
                html.Hr(style={"margin": "6px 0"}),
                html.Small(f"🎯 OBJETIVO GENERAL: {info_est['objetivo']}", className="text-muted font-italic", style={"fontSize": "0.75rem"})
            ], color="light", className="mt-2 mb-3 border-start border-primary", style={'borderLeftWidth': '4px'})

            store_pagina = dcc.Store(id='store-pagina-actual', data=1)

            # EVALUACIÓN DIRECTA DE MATRIZ MIR
            columnas_lower = [str(c).lower() for c in df.columns]
            es_matriz_mir = any("eje" in c or "programa presupuestario" in c or "nivel" in c for c in columnas_lower) or "MIR" in tabla.upper() or "RECEPCION" in tabla.upper()

            if es_matriz_mir:
                # Inyección directa de la vista rediseñada
                vista_tabla = diseñar_tabla_mir_consolidada(df)
            else:
                vista_tabla = html.Div(id='contenedor-tabla-paginada')

            contenido = html.Div([
                store_pagina,
                dbc.Row([
                    dbc.Col(html.H2(f"📊 {nombre_area}", className="text-primary font-weight-bold", style={"fontSize": "1.3rem"}), md=9),
                    dbc.Col(html.Div(id='notif-area'), md=3)
                ], className="mb-2 align-items-center"),
                
                bloque_resumen,
                vista_tabla,
                seccion_impacto_layout()
            ])
            return contenido, {'tabla': tabla, 'id': idx}, resumen_cards
        except Exception as e:
            if 'conn' in locals(): conn.close()
            return dbc.Alert(f"Error al estructurar el tablero: {e}", color="danger"), no_update, ""

    # --- CAMBIO DE PÁGINA EN TABLA OPERATIVA ---
    @app.callback(
        Output('store-pagina-actual', 'data'),
        [
            Input('btn-pag-inicio', 'n_clicks'),
            Input('btn-pag-prev', 'n_clicks'),
            Input('btn-pag-next', 'n_clicks'),
            Input('btn-pag-fin', 'n_clicks')
        ],
        [
            State('store-pagina-actual', 'data'),
            State('active-info', 'data')
        ],
        prevent_initial_call=True
    )
    def cambiar_pagina(btn_inicio, btn_prev, btn_next, btn_fin, pag_actual, active_info):
        ctx = dash.callback_context
        if not ctx.triggered or not active_info:
            return no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        conn = sqlite3.connect(DB_GESTION)
        df_count = pd.read_sql_query(f'SELECT COUNT(*) as total FROM "{active_info["tabla"]}"', conn)
        conn.close()
        
        total_registros = df_count.iloc[0]['total']
        total_paginas = math.ceil(total_registros / TAMANO_PAGINA) if total_registros > 0 else 1

        if trigger_id == 'btn-pag-inicio':
            return 1
        elif trigger_id == 'btn-pag-prev':
            return max(1, pag_actual - 1)
        elif trigger_id == 'btn-pag-next':
            return min(total_paginas, pag_actual + 1)
        elif trigger_id == 'btn-pag-fin':
            return total_paginas

        return pag_actual

    # --- RENDERIZADO PAGINADO DE TABLAS OPERATIVAS ---
    @app.callback(
        Output('contenedor-tabla-paginada', 'children'),
        [Input('store-pagina-actual', 'data'), Input('contenido-area', 'children')],
        State('active-info', 'data')
    )
    def renderizar_tabla_paginada(pag_actual, _, active_info):
        if not active_info:
            return no_update
        
        conn = sqlite3.connect(DB_GESTION)
        try:
            df = pd.read_sql_query(f'SELECT rowid, * FROM "{active_info["tabla"]}"', conn)
            conn.close()
            
            columnas_lower = [str(c).lower() for c in df.columns]
            if any("eje" in c or "programa presupuestario" in c or "nivel" in c for c in columnas_lower) or "MIR" in active_info["tabla"].upper() or "RECEPCION" in active_info["tabla"].upper():
                return no_update
                
            return construir_tabla_estilo_cards(df, pagina_actual=pag_actual or 1)
        except Exception:
            conn.close()
            return no_update

    @app.callback(
        Output('contenedor-graficas-impacto', 'children'),
        Input('contenido-area', 'children'),
        State('active-info', 'data')
    )
    def actualizar_graficas(_, info):
        if not info: 
            return no_update
        conn = sqlite3.connect(DB_GESTION)
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{info["tabla"]}"', conn)
            conn.close()
            return generar_tablero_impacto(df, nombre_tabla=info['tabla'])
        except Exception:
            conn.close()
            return no_update
