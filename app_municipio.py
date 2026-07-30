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

# Definición de ruta absoluta para la carpeta de estilos
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
RUTA_ASSETS = os.path.join(DIRECTORIO_RAIZ, "assets")

# 2. Configurar la App Dash
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.LUX, 
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
    ], 
    assets_folder=RUTA_ASSETS,        # Fuerza la ruta absoluta de la carpeta assets
    include_assets_files=True,       # Carga automática de los archivos CSS locales
    suppress_callback_exceptions=True
)
app.title = "Sistema de Gestión Municipal PbR - PMD"

# 3. Construir el Layout Principal unificado y limpio (Eliminando el header duplicado)
# Llamamos directamente a servir_layout() que ya contiene un Navbar limpio y profesional.
app.layout = servir_layout()

# 4. Registrar todos los callbacks importados desde la carpeta /callbacks
register_mir_callbacks(app)
register_navegacion_callbacks(app)
register_admin_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
