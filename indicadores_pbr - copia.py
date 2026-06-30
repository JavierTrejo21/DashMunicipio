# indicadores_pbr.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px

def calcular_indicadores_pbr(df):
    """
    Analizador Avanzado de Desempeño PbR Municipal.
    Calcula eficacia, eficiencia financiera y genera el Semáforo Institucional MIR.
    """
    if df is None or df.empty:
        return None

    # Homologar columnas a mayúsculas para evitar errores de dedo
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().upper() for c in df_clean.columns]
    
    # Identificación predictiva de columnas
    col_atn = next((c for c in df_clean.columns if "ATEN" in c or "BENE" in c), None)
    col_inv = next((c for c in df_clean.columns if "INV" in c or "PRESU" in c), None)
    col_act = next((c for c in df_clean.columns if "ACT" in c), "ACTIVIDAD")
    col_var = next((c for c in df_clean.columns if "VAR" in c), None)

    # Conversión a datos numéricos seguros
    if col_atn:
        df_clean[col_atn] = pd.to_numeric(df_clean[col_atn], errors='coerce').fillna(0)
    if col_inv:
        df_clean[col_inv] = pd.to_numeric(df_clean[col_inv], errors='coerce').fillna(0)

    # --- LÓGICA REVOLUCIONADA DEL PbR ---
    # En lugar de contar filas, evaluamos la relación Realizado vs Programado si existe la columna VARIABLE
    if col_var and 'VARIABLE' in df_clean.columns:
        realizados = df_clean[df_clean[col_var].str.contains("REALIZADO|APROBADO", na=False, case=False)]
        totales = len(df_clean)
        alcanzadas = len(realizados)
    else:
        # Si no hay estatus, evaluamos por registros con impacto (atendidos > 0)
        totales = len(df_clean)
        alcanzadas = len(df_clean[df_clean[col_atn] > 0]) if col_atn else totales

    # Calcular Porcentaje de Cumplimiento Eficaz
    porcentaje = round((alcanzadas / totales) * 100, 1) if totales > 0 else 0
    
    # Determinación del Semáforo Oficial (MIR)
    if porcentaje >= 90:
        color_semaforo = "success"  # Verde
        texto_semaforo = "🟢 DESEMPEÑO ÓPTIMO (CUMPLE METAS)"
        badge_color = "#2ecc71"
    elif porcentaje >= 70:
        color_semaforo = "warning"  # Amarillo
        texto_semaforo = "🟡 EN OBSERVACIÓN (REZAGO MODERADO)"
        badge_color = "#f1c40f"
    else:
        color_semaforo = "danger"   # Rojo
        texto_semaforo = "🔴 ALERTA CRÍTICA (INCUMPLIMIENTO DE PLAN)"
        badge_color = "#e74c3c"

    # Presupuesto e Inversión Total
    inversion_total = df_clean[col_inv].sum() if col_inv else 0
    beneficiarios_totales = df_clean[col_atn].sum() if col_atn else 0
    costo_por_beneficiario = round(inversion_total / beneficiarios_totales, 2) if beneficiarios_totales > 0 else 0

    # --- INTERFAZ VISUAL PREMIUM DEL PbR ---
    componente_visual = html.Div([
        # Encabezado del Bloque PbR
        html.Div([
            html.Span(texto_semaforo, style={"fontWeight": "bold", "color": "#1f2937", "fontSize": "0.9rem"}),
            html.Span(f"Evaluación PbR Periodo Actual", className="text-muted float-end", style={"fontSize": "0.75rem"})
        ], className="p-2 border-bottom mb-3 bg-light", style={"borderRadius": "6px 6px 0 0"}),

        # Fila de Tarjetas Ejecutivas
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Small("EFICACIA DE METAS", className="text-muted d-block font-weight-bold", style={"fontSize": "0.65rem"}),
                    html.H4(f"{porcentaje}%", style={"color": badge_color, "fontWeight": "bold", "margin": "0"}),
                    html.Small(f"{alcanzadas} de {totales} acciones cubiertas", className="text-muted", style={"fontSize": "0.6rem"})
                ], className="bg-white p-3 border text-center shadow-sm", style={"borderRadius": "8px"}), md=4, className="mb-2"
            ),
            dbc.Col(
                html.Div([
                    html.Small("PRESUPUESTO EJERCIDO", className="text-muted d-block font-weight-bold", style={"fontSize": "0.65rem"}),
                    html.H4(f"${inversion_total:,.2f}", style={"color": "#691c32", "fontWeight": "bold", "margin": "0"}),
                    html.Small("Inversión social registrada", className="text-muted", style={"fontSize": "0.6rem"})
                ], className="bg-white p-3 border text-center shadow-sm", style={"borderRadius": "8px"}), md=4, className="mb-2"
            ),
            dbc.Col(
                html.Div([
                    html.Small("COSTE PAR CITADANO", className="text-muted d-block font-weight-bold", style={"fontSize": "0.65rem"}),
                    html.H4(f"${costo_por_beneficiario:,.2f}", style={"color": "#bc955c", "fontWeight": "bold", "margin": "0"}),
                    html.Small("Inversión promedio por beneficiario", className="text-muted", style={"fontSize": "0.6rem"})
                ], className="bg-white p-3 border text-center shadow-sm", style={"borderRadius": "8px"}), md=4, className="mb-2"
            ),
        ]),
    ], className="mb-4 p-1")

    return componente_visual
