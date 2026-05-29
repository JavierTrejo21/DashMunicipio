import dash_bootstrap_components as dbc
from dash import dcc, html

def servir_layout():
    """Define la estructura principal de la aplicación (Sidebar y Contenedor Principal)"""
    return dbc.Container([
        # Almacenamiento de datos de sesión
        dcc.Store(id='active-info'), 
        
        # --- HEADER / NAVBAR ---
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Configuración", id="btn-abrir-config", n_clicks=0, className="text-white")),
                dbc.NavItem(dbc.NavLink("Actualizar Datos", id="btn-abrir-update", n_clicks=0, className="text-white")),
                dbc.NavItem(dbc.NavLink("Eliminar Sección", id="btn-abrir-borrado-seccion", n_clicks=0, className="text-white", style={"color": "#ff4d4d !important"})),
            ],
            brand="SISTEMA DE GESTIÓN MUNICIPAL | PbR - PMD",
            brand_href="#",
            color="#691c32", # Color institucional
            dark=True,
            className="mb-4 shadow-sm rounded-bottom"
        ),

        # --- SECCIÓN DE ACUERDOS (Selección Inicial) ---
        html.Div([
            html.H5("📂 EJES ESTRATÉGICOS (PMD)", className="text-muted mb-3 font-weight-bold"),
            dbc.Row(id='contenedor-tarjetas-acuerdos', className="mb-4"),
        ]),

        # --- SECCIÓN DE ÁREAS (Desplegable) ---
        dbc.Collapse(
            id='collapse-areas',
            children=[
                html.Div([
                    html.H5("🏢 ÁREAS ADMINISTRATIVAS", className="text-muted mb-3 font-weight-bold"),
                    html.Div(id='contenedor-botones-areas', className="d-flex flex-wrap mb-4")
                ], className="p-3 bg-light rounded shadow-sm mb-4")
            ]
        ),

        # --- DASHBOARD DINÁMICO ---
        # Aquí se inyectan las Tarjetas KPI
        html.Div(id='resumen-kpis', className="mb-4"),
        
        # Aquí se inyecta la Tabla y el Tablero de Resultados
        html.Div(id='contenido-area'),

        # --- MODALES DE GESTIÓN ---
        modal_configuracion(),
        modal_actualizacion(),
        modal_borrado()
        
    ], fluid=True, className="p-4 bg-white", style={"minHeight": "100vh"})

# --- COMPONENTE: MODAL NUEVA ÁREA ---
def modal_configuracion():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Configurar Nueva Área de Gestión")),
        dbc.ModalBody([
            dbc.Label("Nombre del Área / Dirección:"),
            dbc.Input(id="input-nombre-area", placeholder="Ej: Obras Públicas, Salud, etc.", type="text", className="mb-3"),
            
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
                ], className="mb-3"
            ),
            
            dbc.Label("Fuente de Datos (Excel o Google Sheets):"),
            dbc.Textarea(
                id="area-texto-excel", 
                style={'height': '200px'},
                placeholder="Pega aquí el contenido de Excel (con encabezados) o la URL de Google Sheets (Acceso Público)...",
                className="mb-2"
            ),
            html.Small("Nota: Si usas Google Sheets, asegúrate de que el acceso sea 'Cualquier persona con el enlace'.", className="text-muted"),
            html.Div(id="salida-confirmacion", className="mt-3")
        ]),
        dbc.ModalFooter(
            dbc.Button("Vincular y Crear Área", id="btn-guardar-excel", color="primary", className="w-100")
        ),
    ], id="modal-config", size="lg")

# --- COMPONENTE: MODAL ACTUALIZAR DATOS ---
def modal_actualizacion():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Sincronizar / Agregar Datos")),
        dbc.ModalBody([
            dbc.Label("Seleccione el Área a actualizar:"),
            dbc.Select(id="update-area-selector", className="mb-3"),
            
            dbc.Label("Nuevos Datos o URL de Sheets:"),
            dbc.Textarea(id="update-texto-excel", style={'height': '150px'}, className="mb-3"),
            html.Div(id="update-status")
        ]),
        dbc.ModalFooter(
            dbc.Button("Actualizar Información", id="btn-update-validar", color="success", className="w-100")
        ),
    ], id="modal-update")

# --- COMPONENTE: MODAL BORRAR ---
def modal_borrado():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Eliminar Sección Administrativa", className="text-danger")),
        dbc.ModalBody([
            html.P("⚠️ Esta acción eliminará permanentemente la tabla de datos y el acceso al área seleccionada."),
            dbc.Select(id="borrar-area-selector", className="mb-3"),
            html.Div(id="borrar-status")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cerrar-borrado", color="secondary"),
            dbc.Button("Confirmar Eliminación", id="btn-confirmar-borrado-final", color="danger")
        ]),
    ], id="modal-borrado-admin")
