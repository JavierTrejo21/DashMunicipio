import dash_bootstrap_components as dbc
from dash import dcc, html


def servir_layout():
    """Define la estructura principal de la aplicación con un diseño unificado y funcional"""
    return dbc.Container(
        [
            # Almacenamiento de datos de sesión
            dcc.Store(id="active-info"),
            
            # --- HEADER / NAVBAR INSTITUCIONAL ÚNICO ---
            dbc.Navbar(
                dbc.Container(
                    [
                        html.Div(
                            [
                                html.I(className="bi bi-bank2 text-white me-2 fs-5"),
                                html.Span(
                                    "SISTEMA DE GESTIÓN MUNICIPAL | PbR - PMD",
                                    className="text-white fw-bold",
                                    style={"font-size": "0.95rem", "letter-spacing": "0.5px"}
                                ),
                            ],
                            className="d-flex align-items-center"
                        ),
                        html.Div(
                            [
                                dbc.Button(
                                    [html.I(className="bi bi-gear-fill me-1"), "Configuración"],
                                    id="btn-abrir-config",
                                    n_clicks=0,
                                    color="link",
                                    className="text-white text-decoration-none px-2 py-0",
                                    style={"font-size": "0.8rem", "font-weight": "600"}
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-arrow-clockwise me-1"), "Actualizar Datos"],
                                    id="btn-abrir-update",
                                    n_clicks=0,
                                    color="link",
                                    className="text-white text-decoration-none px-2 py-0",
                                    style={"font-size": "0.8rem", "font-weight": "600"}
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-trash-fill me-1"), "Eliminar Sección"],
                                    id="btn-abrir-borrado-seccion",
                                    n_clicks=0,
                                    color="link",
                                    className="text-decoration-none px-2 py-0",
                                    style={"font-size": "0.8rem", "font-weight": "600", "color": "#FCA5A5 !important"}
                                ),
                            ],
                            className="d-flex align-items-center gap-2"
                        )
                    ],
                    fluid=True,
                    className="px-2"
                ),
                color="#691c32",
                dark=True,
                className="mb-4 shadow-sm py-2",
                style={"border-bottom": "3px solid #4A1322"}
            ),

            # --- SECCIÓN COLAPSIBLE: MATRIZ MIR GENERAL (ALTA DIRECCIÓN) ---
            html.Div([
                dbc.Button(
                    [
                        html.I(className="bi bi-file-earmark-bar-graph-fill me-2", style={"color": "#0F766E"}), 
                        "VER MATRIZ MIR GENERAL (ALTA DIRECCIÓN)"
                    ],
                    id="btn-toggle-mir-superior",
                    n_clicks=0,
                    className="w-100 mb-2 py-2.5 d-flex align-items-center justify-content-center",
                    style={
                        "background-color": "#FFFFFF",
                        "color": "#1E293B",
                        "border": "1px solid #E2E8F0",
                        "border-radius": "10px",
                        "font-weight": "700",
                        "font-size": "0.82rem",
                        "box-shadow": "0 2px 5px rgba(0, 0, 0, 0.02)",
                        "transition": "all 0.2s ease-in-out"
                    }
                ),
                dbc.Collapse(
                    id="collapse-mir-superior",
                    is_open=False,
                    children=html.Div(id="seccion-superior-mir-consolidada", className="mb-4")
                )
            ], className="mb-3"),

            # --- SECCIÓN DE ACUERDOS (EJES ESTRATÉGICOS) ---
            html.Div([
                html.H5(
                    "📂 EJES ESTRATÉGICOS (PMD)",
                    className="text-muted mb-3 fw-bold",
                    style={"font-size": "0.82rem", "letter-spacing": "0.5px"}
                ),
                dbc.Row(id="contenedor-tarjetas-acuerdos", className="mb-4 g-3"),
            ]),

            # --- SECCIÓN DE ÁREAS (Desplegable) ---
            dbc.Collapse(
                id="collapse-areas",
                children=[
                    html.Div(
                        [
                            html.H5(
                                "🏢 ÁREAS ADMINISTRATIVAS",
                                className="text-muted mb-3 fw-bold",
                                style={"font-size": "0.82rem", "letter-spacing": "0.5px"}
                            ),
                            html.Div(
                                id="contenedor-botones-areas",
                                className="d-flex flex-wrap gap-2 mb-4",
                            ),
                        ],
                        className="p-3 bg-white border border-light rounded-3 shadow-sm mb-4",
                    )
                ],
            ),

            # --- DASHBOARD DINÁMICO ---
            html.Div(id="resumen-kpis", className="mb-4"),
            html.Div(id="contenido-area"),

            # --- MODALES DE GESTIÓN ---
            modal_configuracion(),
            modal_actualizacion(),
            modal_borrado(),
        ],
        fluid=True,
        className="p-4 bg-light",
        style={"minHeight": "100vh"},
    )


# --- COMPONENTE: MODAL NUEVA ÁREA ---
def modal_configuracion():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Configurar Nueva Área de Gestión")
            ),
            dbc.ModalBody([
                dbc.Label("Nombre del Área / Dirección:"),
                dbc.Input(
                    id="input-nombre-area",
                    placeholder="Ej: Obras Públicas, Salud, etc.",
                    type="text",
                    className="mb-3",
                ),
                dbc.Label("Vincular a Eje Estratégico:"),
                dbc.Select(
                    id="input-acuerdo-id",
                    options=[
                        {"label": "1. GOBIERNO PARTICIPATIVO Y TRANSFORMADOR", "value": 1},
                        {"label": "2. BIENESTAR Y PROSPERIDAD", "value": 2},
                        {"label": "3. DESARROLLO ECONÓMICO Y CULTURAL", "value": 3},
                        {"label": "4. DESARROLLO SOSTENIBLE E INFRAESTRUCTURA", "value": 4},
                        {"label": "5. IGUALDAD Y DERECHOS HUMANOS", "value": 5},
                        {"label": "6. GOBIERNO TECNOLÓGICO Y DIGITAL", "value": 6},
                        {"label": "7. TRANSPARENCIA Y RENDICIÓN DE CUENTAS", "value": 7},
                    ],
                    className="mb-3",
                ),
                dbc.Label("Fuente de Datos (Excel o Google Sheets):"),
                dbc.Textarea(
                    id="area-texto-excel",
                    style={"height": "200px"},
                    placeholder="Pega aquí el contenido de Excel o URL de Google Sheets...",
                    className="mb-2",
                ),
                html.Div(id="salida-confirmacion", className="mt-3"),
            ]),
            dbc.ModalFooter(
                dbc.Button(
                    "Vincular y Crear Área",
                    id="btn-guardar-excel",
                    color="primary",
                    className="w-100",
                )
            ),
        ],
        id="modal-config",
        size="lg",
    )


# --- COMPONENTE: MODAL ACTUALIZAR DATOS ---
def modal_actualizacion():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Sincronizar / Agregar Datos")),
            dbc.ModalBody([
                dbc.Label("Seleccione el Área a actualizar:"),
                dbc.Select(id="update-area-selector", className="mb-3"),
                dbc.Label("Nuevos Datos o URL de Sheets:"),
                dbc.Textarea(
                    id="update-texto-excel",
                    style={"height": "150px"},
                    className="mb-3",
                ),
                html.Div(id="update-status"),
            ]),
            dbc.ModalFooter(
                dbc.Button(
                    "Actualizar Información",
                    id="btn-update-validar",
                    color="success",
                    className="w-100",
                )
            ),
        ],
        id="modal-update",
    )


# --- COMPONENTE: MODAL BORRAR ---
def modal_borrado():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Eliminar Sección Administrativa", className="text-danger")
            ),
            dbc.ModalBody([
                html.P("⚠️ Esta acción eliminará permanentemente la tabla y el acceso al área."),
                dbc.Select(id="borrar-area-selector", className="mb-3"),
                html.Div(id="borrar-status"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="btn-cerrar-borrado", color="secondary"),
                dbc.Button("Confirmar Eliminación", id="btn-confirmar-borrado-final", color="danger"),
            ]),
        ],
        id="modal-borrado-admin",
    )
