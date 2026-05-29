import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

# Importar el mapa centralizado
from analisis_estrategico import MAPEO_ANALISIS

GUINDA_INST = "#691c32"      
DORADO_INST = "#bc955c"      
TEXTO_DARK = "#1f2937"

def generar_tablero_impacto(df, nombre_tabla=None):
    """
    Enrutador principal de analíticas. Si detecta la llave especializada,
    le entrega el control absoluto a analisis_estrategico.py
    """
    if df is None or df.empty:
        return dbc.Alert("No existen registros suficientes en esta sección.", color="light", className="p-3 text-muted")

    # Estandarizar el nombre de la tabla eliminando acentos, espacios o guiones sueltos
    tabla_limpia = str(nombre_tabla).strip().upper().replace("-", "_").replace(" ", "_")

    # 1. DIRECCIONAMIENTO: Si coincide con nuestra tabla premium, inyectar el diseño limpio
    if tabla_limpia in MAPEO_ANALISIS:
        try:
            return MAPEO_ANALISIS[tabla_limpia](df)
        except Exception as e:
            return dbc.Alert(f"⚠️ Error al construir estadísticas premium: {e}", color="danger")

    # 2. RESPALDO GENERAL AUTOMÁTICO (Para las demás áreas que aún no se personalizan)
    columnas = df.columns
    col_x = columnas[1] if len(columnas) > 1 else columnas[0]
    col_y = "Inversión" if "Inversión" in columnas else (columnas[3] if len(columnas) > 3 else columnas[-1])
    
    try:
        df[col_y] = pd.to_numeric(df[col_y], errors='coerce').fillna(0)
        df_resumen = df.groupby(col_x)[col_y].sum().reset_index().sort_values(by=col_y, ascending=False).head(10)
        
        fig_auto = px.bar(df_resumen, x=col_x, y=col_y, color_discrete_sequence=[GUINDA_INST])
        fig_auto.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(t=20, b=20, l=40, r=20),
            xaxis=dict(tickfont=dict(size=9)), yaxis=dict(gridcolor="#f3f4f6")
        )
        return html.Div([
            html.H6(f"📊 HISTOGRAMA AUTOMÁTICO: {str(col_y).upper()} POR {str(col_x).upper()} (TOP 10)", className="font-weight-bold text-muted mb-2", style={"fontSize": "0.75rem"}),
            dcc.Graph(figure=fig_auto, config={'displayModeBar': False})
        ], className="bg-white border p-3 shadow-sm", style={'borderRadius': '18px'})
    except:
        return dbc.Alert("Métricas en proceso de diseño institucional.", color="light", className="p-3 text-center text-muted")


def seccion_impacto_layout():
    """Línea divisional y contenedor base"""
    return html.Div([
        html.Div(style={'borderTop': f'3px solid {DORADO_INST}', 'width': '80px', 'margin': '40px 0 20px 15px'}),
        html.Div([
            html.H3("SISTEMA DE EVALUACIÓN Y RENDICIÓN DE CUENTAS", className="font-weight-bold text-dark mb-1", style={'fontSize': '1.1rem', 'letterSpacing': '0.5px'}),
            html.P("Evidencia analítica de impacto social directo asociada a los objetivos institucionales.", className="text-muted", style={'fontSize': '0.8rem'})
        ], style={'paddingLeft': '15px', 'marginBottom': '25px'}),
        
        html.Div(id='contenedor-graficas-impacto')
    ])
