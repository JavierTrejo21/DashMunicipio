import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
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
    """Genera el contenedor visual unificado e integrado para la sección de evaluación y rendición de cuentas."""
    return html.Div([
        html.Div(
            [
                # Encabezado interno de la sección
                html.Div(
                    [
                        html.Div(
                            style={
                                "width": "35px",
                                "height": "4px",
                                "backgroundColor": "#1ca2a9",
                                "borderRadius": "2px",
                                "marginBottom": "10px",
                            }
                        ),
                        html.H4(
                            "SISTEMA DE EVALUACIÓN Y RENDICIÓN DE CUENTAS",
                            className="m-0",
                            style={
                                "fontSize": "1rem",
                                "fontWeight": "700",
                                "color": "#691c32",
                                "letterSpacing": "0.3px",
                            },
                        ),
                        html.P(
                            "Evidencia analítica de impacto social directo asociada a los objetivos institucionales.",
                            className="m-0 text-muted mt-1",
                            style={"fontSize": "0.8rem", "fontWeight": "500"},
                        ),
                    ],
                    className="pb-3 mb-3",
                    style={"borderBottom": "1px solid #f1f5f9"}
                ),
                
                # Contenedor donde se cargan dinámicamente las gráficas de impacto
                html.Div(id='contenedor-graficas-impacto')
            ],
            className="p-4 bg-white shadow-sm mt-4",
            style={
                "borderTop": "5px solid #1ca2a9",
                "borderRadius": "10px",
                "borderLeft": "1px solid #dee2e6",
                "borderRight": "1px solid #dee2e6",
                "borderBottom": "1px solid #dee2e6",
            },
        )
    ])