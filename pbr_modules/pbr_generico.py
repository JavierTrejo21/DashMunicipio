# pbr_modules/pbr_generico.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

def calcular_pbr_generico(df):
    """Módulo de Respaldo por defecto para asegurar la estabilidad del sistema"""
    totales = len(df)
    return dbc.Alert([
        html.H6("📋 SISTEMA DE MONITOREO DE ACTIVIDADES", className="font-weight-bold mb-1", style={"fontSize": "0.85rem"}),
        html.P(f"Se han detectado {totales} líneas de acción registradas en esta base de datos. Modifique el paquete 'pbr_modules' para asignar una Matriz de Indicadores (MIR) específica a esta dirección municipal.", className="mb-0", style={"fontSize": "0.75rem"})
    ], color="secondary", className="border-start border-secondary mb-3")
