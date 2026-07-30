import sys
import os

# Forzar a Python a incluir el directorio actual en el PATH de búsqueda
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import dash
from dash import html
import dash_bootstrap_components as dbc

# Módulos locales de configuración y layout
from database import inicializar_db
from layouts import servir_layout

# Importar los registradores de callbacks independientes
from callbacks.cb_mir import register_mir_callbacks
from callbacks.cb_navegacion import register_navegacion_callbacks
from callbacks.cb_admin import register_admin_callbacks

# 1. Inicializar la base de datos de SQLite
inicializar_db()

# 2. Configurar la App Dash
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.LUX, dbc.icons.BOOTSTRAP], 
    suppress_callback_exceptions=True
)
app.title = "Sistema de Gestión Municipal PbR - PMD"

# 3. Construir el Layout Principal con el desplegable MIR
layout_original = servir_layout()

bloque_desplegable_mir = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Button(
                "📊 Ver Matriz MIR General (Alta Dirección)", 
                id="btn-toggle-mir-superior", 
                color="dark", 
                outline=True,
                className="w-100 my-2 font-weight-bold shadow-sm",
                style={"borderRadius": "10px", "fontSize": "0.85rem", "letterSpacing": "1px"}
            ),
            width=12
        )
    ]),
    dbc.Collapse(
        id="collapse-mir-superior",
        is_open=False,
        children=html.Div(id="seccion-superior-mir-consolidada")
    )
], fluid=True, className="px-4 mb-3")

if hasattr(layout_original, 'children') and isinstance(layout_original.children, list):
    layout_original.children.insert(2, bloque_desplegable_mir)
    app.layout = layout_original
else:
    app.layout = html.Div([
        layout_original,
        bloque_desplegable_mir
    ])

# 4. Registrar todos los callbacks importados desde la carpeta /callbacks
register_mir_callbacks(app)
register_navegacion_callbacks(app)
register_admin_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
