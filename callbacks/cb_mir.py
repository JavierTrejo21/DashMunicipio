# callbacks/cb_mir.py
from dash import Input, Output, State, html
from areas.mir_general import analizar_mir_general, generar_tabla_resumen_area

RUTA_CSV_MIR = r"C:\DashMunicipio\DES01_CHU_02_2026.xlsx"


def register_mir_callbacks(app):

    # ==========================================
    # 1. TOGGLE DE LA MATRIZ MIR GENERAL
    # ==========================================
    @app.callback(
        Output("collapse-mir-superior", "is_open"),
        [Input("btn-toggle-mir-superior", "n_clicks")],
        [State("collapse-mir-superior", "is_open")],
        prevent_initial_call=True,
    )
    def cb_toggle_mir(n_clicks, esta_abierto):
        if n_clicks:
            return not esta_abierto
        return esta_abierto

    # ==========================================
    # 2. CARGA DE LA MATRIZ GENERAL CONSOLIDADA
    # ==========================================
    @app.callback(
        Output("seccion-superior-mir-consolidada", "children"),
        Input("collapse-mir-superior", "is_open"),
    )
    def cb_cargar_mir_dinamica(esta_abierto):
        if esta_abierto:
            return analizar_mir_general(RUTA_CSV_MIR)
        return html.Div()

    # ==========================================
    # 3. CARGA DINÁMICA DE LA TABLA RESUMEN POR ÁREA
    # ==========================================
    @app.callback(
        Output("contenedor-resumen-area", "children"),
        Input("contenido-area", "children"),
        prevent_initial_call=True,
    )
    def cb_cargar_resumen_area(contenido_activo):
        if not contenido_activo:
            return html.Div()

        try:
            # 🔍 PASO DE DIAGNÓSTICO: Buscamos cualquier texto dentro del contenido activo para no fallar
            nombre_area = "RECEPCIÓN" # Forzamos una búsqueda inicial de prueba si falla la extracción automatizada
            
            if isinstance(contenido_activo, dict):
                props = contenido_activo.get("props", {})
                children = props.get("children", [])
                # Intentamos extraer de manera flexible
                str_contenido = str(children)
                if "PRESIDENCIA" in str_contenido.upper():
                    nombre_area = "PRESIDENCIA"
                elif "MUNICIPAL" in str_contenido.upper():
                    nombre_area = "MUNICIPAL"

            # Llamamos directamente a la función de la MIR
            resultado = generar_tabla_resumen_area(RUTA_CSV_MIR, nombre_area)

            # Retornamos de manera directa y forzada con el nuevo diseño institucional para verificar que se pinte en pantalla
            return html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-bar-chart-fill me-2", style={"color": "#1ca2a9"}),
                            html.Span(
                                "Relación de indicadores específicos referenciados al área en relación a la MIR",
                                style={
                                    "color": "#781d37",
                                    "fontWeight": "bold",
                                    "fontSize": "0.95rem",
                                    "letterSpacing": "0.5px"
                                }
                            )
                        ],
                        className="p-3 mb-3 bg-white rounded-3 shadow-sm d-flex align-items-center",
                        style={"borderLeft": "4px solid #920d24"}
                    ),
                    resultado
                ]
            )
        except Exception as e:
            # Si algo falla, te mostrará el error exacto en pantalla en lugar de quedarse en blanco
            return html.Div(f"⚠️ Error controlado en callback MIR: {e}", className="alert alert-danger")
