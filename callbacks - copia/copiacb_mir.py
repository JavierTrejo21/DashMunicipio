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
            nombre_area = ""
            if isinstance(contenido_activo, dict):
                props = contenido_activo.get("props", {})
                children = props.get("children", [])
                if isinstance(children, list) and len(children) > 0:
                    card_body = children[0].get("props", {}).get("children", [])
                    for elem in card_body:
                        if isinstance(elem, dict) and elem.get("type") == "H3":
                            nombre_area = elem.get("props", {}).get("children", "")
                            break

            # Validar que exista el nombre del área
            if nombre_area and str(nombre_area).strip() not in ["", "None", "📊"]:
                resultado = generar_tabla_resumen_area(RUTA_CSV_MIR, nombre_area)
                
                # 🛡️ FILTRO ANTI-BANNER BEIGE:
                # Detecta si el componente generado por mir_general.py es un Alert / Aviso beige
                es_alerta = False
                if hasattr(resultado, "color"):
                    es_alerta = True
                elif isinstance(resultado, dict):
                    es_alerta = resultado.get("type") in ["Alert", "dbc.Alert"] or "color" in resultado.get("props", {})

                # Si es una alerta beige, retornamos un Div vacío para ocultarla por completo
                if es_alerta:
                    return html.Div()

                return resultado
        except Exception:
            pass

        return html.Div()
