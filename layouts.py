import dash_bootstrap_components as dbc
from dash import dcc, html

def servir_layout():
    """
    Define la estructura principal con el Rediseño V4:
    Estilo institucional, tipografías clásicas y grilla de ejes estratégicos.
    """
    return html.Div([
        # --- RECURSOS EXTERNOS (Fuentes) ---
        html.Link(href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap", rel="stylesheet"),
        
                # Almacenamiento de datos de sesión y componente de descarga
        dcc.Store(id="active-info"),
        dcc.Download(id="download-excel-mir-original"),
        dcc.Download(id="download-reporte-eje"),


        # --- TOPBAR (Estilo Institucional) ---
        html.Div([
            html.Div([
                html.I(className="bi bi-bank2 me-2", style={"color": "#B5892C", "fontSize": "18px"}),
                html.Span("SISTEMA DE GESTIÓN MUNICIPAL | PbR – PMD", className="fw-bold")
            ], className="topbar-title"),
            
            html.Div([
                html.Span([html.I(className="bi bi-gear me-1"), "Configuración"], 
                          id="btn-abrir-config", className="cursor-pointer opacity-90 mx-3", style={"cursor": "pointer"}),
                html.Span([html.I(className="bi bi-arrow-clockwise me-1"), "Actualizar"], 
                          id="btn-abrir-update", className="cursor-pointer opacity-90 mx-3", style={"cursor": "pointer"}),
                html.Span([html.I(className="bi bi-trash me-1"), "Eliminar"], 
                          id="btn-abrir-borrado-seccion", className="cursor-pointer opacity-90 mx-3", style={"cursor": "pointer", "color": "#FCA5A5"}),
            ], className="d-flex align-items-center", style={"fontSize": "11.5px", "fontWeight": "500"})
        ], className="topbar-custom d-flex justify-content-between align-items-center"),

        # --- CONTENEDOR PRINCIPAL ---
        dbc.Container([
            
            # Botón MIR General (Compacto y Elegante)
            html.Div([
                dbc.Button([
                    html.I(className="bi bi-file-earmark-text me-2", style={"color": "#B5892C"}), 
                    "Ver Matriz MIR General"
                ], id="btn-toggle-mir-superior", className="card-inst w-100 d-flex align-items-center justify-content-center py-3 mb-4",
                style={"borderLeft": "4px solid #B5892C", "fontSize": "12.5px", "fontWeight": "600", "color": "#5A1530"})
            ]),

            dbc.Collapse(
                id="collapse-mir-superior",
                is_open=False,
                children=html.Div([
                    html.Div([
                        html.Span("📁 MATRIZ DE INDICADORES PARA RESULTADOS (CONSOLIDADA)", className="fw-bold", style={"fontSize": "12px", "color": "#7A1E3D"}),
                        dbc.Button(
                            "Descargar Excel", 
                            id="btn-descargar-mir-original", 
                            color="success", 
                            size="sm", 
                            className="px-3 text-white text-decoration-none",
                            href="https://docs.google.com/spreadsheets/d/11jBjOTf6nqwGzaVMj4AQyR4ApYT2MaYJ/export?format=xlsx",
                            external_link=True,
                            target="_blank"
                        )
                    ], className="d-flex justify-content-between align-items-center bg-white p-3 mb-3 border rounded shadow-sm"),
                    html.Div(id="seccion-superior-mir-consolidada", className="mb-4")
                ])
            ),

            # Etiqueta de Sección
            html.Div([
                html.I(className="bi bi-folder2-open me-2", style={"color": "#B5892C"}),
                html.Span("Ejes Estratégicos (PMD)"),
                html.Div(className="line")
            ], className="section-label-container"),

            # --- GRILLA DE EJES (Mecanismo Hub & Spoke) ---
            html.Div([
                
                # Fila del EJE RECTOR (HUB)
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div([
                                # Progress Ring
                                html.Div([
                                    html.Div([html.I(className="bi bi-diagram-3")], className="badge-inner")
                                ], className="badge-ring", style={"background": "conic-gradient(#B5892C 64%, #E3DDD2 0)"}),
                                
                                html.Div([
                                    html.Div("Eje Rector", className="card-eyebrow"),
                                    html.Div("Gobierno Participativo y Transformador", className="card-name", style={"fontSize": "14.5px"}),
                                    html.Div("Seguimiento estratégico y evaluación de indicadores", className="card-sub"),
                                ], className="card-text")
                            ], className="card-top"),
                            html.Div([
                                html.Span("79.67% de avance", className="pct-tag", style={"color": "#8A6512"}),
                                html.Span([html.I(className="bi bi-bar-chart-line me-1"), "12 indicadores"], className="status-tag")
                            ], className="card-foot")
                        ], id={"type": "tarjeta-eje", "index": 1}, className="card-inst hub mx-auto", style={"maxWidth": "420px"})
                    ], width=12, className="mb-4")
                ]),

                # Fila de Columnas de Ejes y Panel de Áreas
                dbc.Row([
                    # Columna Izquierda (Ejes 2, 3, 4)
                    dbc.Col([
                        crear_tarjeta_eje_v4(2, "Bienestar y Prosperidad", "bi-rocket-takeoff", 62.16, 9),
                        crear_tarjeta_eje_v4(3, "Desarrollo Económico y Cultural", "bi-building-up", 57.41, 7),
                        crear_tarjeta_eje_v4(4, "Desarrollo Sostenible e Infraestructura", "bi-leaf", 52.20, 10),
                    ], md=4, className="d-flex flex-column gap-3"),

                    # Columna Central (Panel de Áreas Dinámico)
                    dbc.Col([
                        dbc.Collapse(
                            id="collapse-areas",
                            is_open=False,
                            children=html.Div([
                                html.Div([
                                    html.I(className="bi bi-folder-fill me-2"),
                                                                        html.Div([
                                        html.Div("Áreas Administrativas", className="fw-bold", style={"fontSize": "12.5px"}),
                                        html.Div(id="titulo-eje-seleccionado", className="opacity-75", style={"fontSize": "10.5px"})
                                    ]),
                                    dbc.Button([
                                        html.I(className="bi bi-file-earmark-pdf me-1"),
                                        "PDF"
                                    ], id="btn-generar-pdf-eje", color="link", size="sm", 
                                    className="ms-auto text-white p-0", style={"fontSize": "11px", "textDecoration": "none"})
                                ], className="areas-head-custom d-flex align-items-center"),

                                html.Div(id="contenedor-botones-areas", className="p-2 d-flex flex-column gap-1")
                            ], className="areas-panel-custom")
                        ),
                        # Mensaje cuando no hay nada seleccionado
                        html.Div(
                            "Seleccione un eje estratégico para ver las áreas administrativas vinculadas.",
                            id="msg-placeholder-areas",
                            className="text-center p-5 text-muted italic",
                            style={"fontSize": "11px", "border": "1px dashed #E3DDD2", "borderRadius": "8px"}
                        )
                    ], md=4),

                    # Columna Derecha (Ejes 5, 6, 7)
                    dbc.Col([
                        crear_tarjeta_eje_v4(5, "Igualdad y Derechos Humanos", "bi-heart-pulse", 35.65, 8),
                        crear_tarjeta_eje_v4(6, "Gobierno Tecnológico y Digital", "bi-laptop", 6.67, 6),
                        crear_tarjeta_eje_v4(7, "Transparencia y Rendición de Cuentas", "bi-shield-check", 18.86, 11),
                    ], md=4, className="d-flex flex-column gap-3"),
                ], className="g-4")
            ], id="contenedor-tarjetas-acuerdos"),

            # --- ÁREA DE CONTENIDO DINÁMICO ---
            html.Div(id="resumen-kpis", className="mt-5"),
            html.Div(id="contenido-area"),

            # Nota al pie
            html.Div([
                html.I(className="bi bi-info-circle me-1"),
                "Cada eje es una tarjeta independiente con su propia insignia de avance. La visualización de indicadores se genera al seleccionar una área específica."
            ], className="mt-5 pb-5 text-muted", style={"fontSize": "11px"})

        ], fluid=True, className="px-4"),

        # Modales
        modal_configuracion(),
        modal_actualizacion(),
        modal_borrado(),
    ], style={"minHeight": "100vh", "backgroundColor": "#EFEDE6"})

def crear_tarjeta_eje_v4(index, nombre, icono, avance, indicadores):
    """Función auxiliar para generar tarjetas con el nuevo estilo V4"""
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([html.I(className=f"bi {icono}")], className="badge-inner")
                ], className="badge-ring", style={"background": f"conic-gradient(#7A1E3D {avance}%, #E3DDD2 0)"}),
                
                html.Div([
                    html.Div(f"Eje 0{index}", className="card-eyebrow"),
                    html.Div(nombre, className="card-name"),
                    html.Div("Seguimiento estratégico", className="card-sub"),
                ], className="card-text")
            ], className="card-top"),
            html.Div([
                html.Span(f"{avance}% de avance", className="pct-tag"),
                html.Span([html.I(className="bi bi-bar-chart-line me-1"), f"{indicadores} indicadores"], className="status-tag")
            ], className="card-foot")
        ], id={"type": "tarjeta-eje", "index": index}, className="card-inst")
    ])

def modal_configuracion():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Configurar Nueva Área", className="playfair")),
        dbc.ModalBody([
            dbc.Label("Nombre del Área:"),
            dbc.Input(id="input-nombre-area", placeholder="Ej: Obras Públicas", className="mb-3"),
            dbc.Label("Vincular a Eje:"),
            dbc.Select(id="input-acuerdo-id", options=[
                {"label": "1. GOBIERNO PARTICIPATIVO", "value": 1},
                {"label": "2. BIENESTAR Y PROSPERIDAD", "value": 2},
                {"label": "3. DESARROLLO ECONÓMICO", "value": 3},
                {"label": "4. DESARROLLO SOSTENIBLE", "value": 4},
                {"label": "5. IGUALDAD Y DH", "value": 5},
                {"label": "6. GOBIERNO DIGITAL", "value": 6},
                {"label": "7. TRANSPARENCIA", "value": 7},
            ], className="mb-3"),
            dbc.Label("Fuente de Datos (URL o Texto):"),
            dbc.Textarea(id="area-texto-excel", style={"height": "150px"}, className="mb-2"),
            html.Div(id="salida-confirmacion")
        ]),
        dbc.ModalFooter(dbc.Button("Vincular y Crear", id="btn-guardar-excel", color="primary", className="w-100"))
    ], id="modal-config", size="lg")

def modal_actualizacion():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Sincronizar Datos")),
        dbc.ModalBody([
            dbc.Select(id="update-area-selector", className="mb-3"),
            dbc.Textarea(id="update-texto-excel", style={"height": "120px"}, className="mb-3"),
            html.Div(id="update-status"),
        ]),
        dbc.ModalFooter(dbc.Button("Actualizar", id="btn-update-validar", color="success", className="w-100")),
    ], id="modal-update")

def modal_borrado():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Eliminar Sección", className="text-danger")),
        dbc.ModalBody([
            html.P("¿Está seguro de eliminar esta área?"),
            dbc.Select(id="borrar-area-selector", className="mb-3"),
            html.Div(id="borrar-status"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cerrar-borrado", color="secondary", className="me-2"),
            dbc.Button("Confirmar", id="btn-confirmar-borrado-final", color="danger")
        ]),
    ], id="modal-borrado-admin")    