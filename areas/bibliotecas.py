# areas/bibliotecas.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_bibliotecas(df):
    """
    Módulo operativo optimizado para Bibliotecas y C.C.A.
    - Cuadrícula compacta de KPIs en 2x2.
    - Tabla nativa HTML con 4 columnas completas (Alineación perfecta).
    - Identidad oficial de Morena (Guinda #73243D y Grises neutros planos).
    - Gráfica lineal comparativa mensual de asistencia abajo.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Bibliotecas llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # LISTA DE ORDEN DE MESES GLOBAL PARA LA FUNCIÓN
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # 1. Copiar y limpiar nombres de columnas
        df_bib = df.copy()
        df_bib.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_bib.columns]

        col_mes = next((c for c in df_bib.columns if "MES" in c), None)
        col_atendidos = next((c for c in df_bib.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_bib.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_bib.columns if "VARIABLE" in c), None)

        # 2. Conversión limpia de tipos de datos
        if col_atendidos:
            df_bib[col_atendidos] = pd.to_numeric(df_bib[col_atendidos], errors='coerce').fillna(0)
            df_bib["CANTIDAD"] = df_bib[col_atendidos]
            col_cantidad_sistema = "CANTIDAD"
        else:
            df_bib["CANTIDAD"] = 0
            col_cantidad_sistema = "CANTIDAD"

        if col_variable: df_bib[col_variable] = df_bib[col_variable].astype(str).str.strip().str.title()
        if col_actividad: df_bib[col_actividad] = df_bib[col_actividad].astype(str).str.strip().str.title()
        if col_mes: df_bib[col_mes] = df_bib[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. CÓMPUTO DE MATRÍCULA REAL (MÁXIMO MENSUAL POR TALLER)
        # =================================================================
        df_grupos = df_bib.groupby([col_actividad, col_variable, col_mes])[col_cantidad_sistema].sum().reset_index() if col_actividad and col_variable and col_mes else pd.DataFrame()
        
        if not df_grupos.empty:
            df_matricula_real = df_grupos.groupby([col_actividad, col_variable])[col_cantidad_sistema].max().reset_index()
            
            total_ninas_activos = df_matricula_real[df_matricula_real[col_variable].str.contains("niña|nina|feme", case=False, na=False)][col_cantidad_sistema].sum()
            total_ninos_activos = df_matricula_real[df_matricula_real[col_variable].str.contains("niño|nino|masc", case=False, na=False)][col_cantidad_sistema].sum()
            total_alumnos_unicos = total_ninas_activos + total_ninos_activos
            
            df_top_talleres = df_matricula_real.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
            top_taller_row = df_top_talleres.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0] if not df_top_talleres.empty else None
            top_programa = str(top_taller_row[col_actividad]) if top_taller_row is not None else "Sin registros"
        else:
            total_alumnos_unicos, total_ninas_activos, total_ninos_activos = 0, 0, 0
            top_programa = "No disponible"

        if len(top_programa) > 35: top_programa = top_programa[:32] + "..."

        # =================================================================
        # 4. DISEÑO DE TARJETAS EN CUADRÍCULA 2x2
        # =================================================================
        estilo_tarjeta = {
            "borderRadius": "6px",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.04)",
            "border": "1px solid #eef2f5",
            "backgroundColor": "#ffffff",
            "padding": "12px 16px",
            "height": "100%"
        }

        cuadrícula_kpis = html.Div([
            html.Div("CUADRO DE MANDO - ALUMNOS MATRICULADOS EN BIBLIOTECAS Y C.C.A.", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#73243D", "marginBottom": "12px", "letterSpacing": "0.8px"}),
            
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("👥 MATRÍCULA TOTAL ACTIVA", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_alumnos_unicos:,.0f} niños(as)", style={"margin": "2px 0", "fontWeight": "700", "color": "#2b6cb0", "fontSize": "18px"}),
                    html.Div("Capacidad real (sin duplicidad)", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("🌟 PROGRAMA CON MAYOR MATRÍCULA", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(top_programa, style={"margin": "2px 0", "fontWeight": "700", "color": "#4a5568", "fontSize": "13px", "lineHeight": "22px"}),
                    html.Div("Grupo fijo más numeroso del año", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),
            ], className="g-2"),

            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("👧 NIÑAS REGISTRADAS (ÚNICAS)", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_ninas_activos:,.0f} alumnas", style={"margin": "2px 0", "fontWeight": "700", "color": "#b83280", "fontSize": "18px"}),
                    html.Div("Comunidad infantil femenina", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("👦 NIÑOS REGISTRADOS (ÚNICAS)", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_ninos_activos:,.0f} alumnos", style={"margin": "2px 0", "fontWeight": "700", "color": "#319795", "fontSize": "18px"}),
                    html.Div("Comunidad infantil masculina", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),
            ], className="g-2")
        ])

        # =================================================================
        # 5. CONSTRUCCIÓN DE LA TABLA (AHORA SÍ CON SUS 4 COLUMNAS REALES)
        # =================================================================
        if not df_matricula_real.empty:
            df_pivot = df_matricula_real.pivot(index=col_actividad, columns=col_variable, values=col_cantidad_sistema).fillna(0).reset_index()
            
            if "Niñas" not in df_pivot.columns: df_pivot["Niñas"] = 0
            if "Niños" not in df_pivot.columns: df_pivot["Niños"] = 0
            
            df_pivot["TOTAL ACTIVO"] = df_pivot["Niñas"] + df_pivot["Niños"]
            df_pivot = df_pivot.sort_values(by="TOTAL ACTIVO", ascending=False)

            filas_tabla = []
            for _, r in df_pivot.iterrows():
                filas_tabla.append(html.Tr([
                    # Columna 1: Taller
                    html.Td(r[col_actividad], style={"fontSize": "11px", "color": "#2d3748", "textAlign": "left", "padding": "8px 14px", "fontWeight": "500", "backgroundColor": "#f9f9f9", "border": "1px solid #cbd5e0"}),
                    # Columna 2: Niñas
                    html.Td(f"{r['Niñas']:,.0f}", style={"fontSize": "11px", "color": "#2d3748", "padding": "8px 14px", "backgroundColor": "#ffffff", "textAlign": "center", "border": "1px solid #cbd5e0"}),
                    # Columna 3: Niños
                    html.Td(f"{r['Niños']:,.0f}", style={"fontSize": "11px", "color": "#2d3748", "padding": "8px 14px", "backgroundColor": "#ffffff", "textAlign": "center", "border": "1px solid #cbd5e0"}),
                    # Columna 4: Total Inscritos (¡AGREGADA PARA EVITAR EL CORTE VISUAL!)
                    html.Td(f"{r['TOTAL ACTIVO']:,.0f}", style={"fontSize": "11px", "color": "#1a202c", "fontWeight": "700", "padding": "8px 14px", "backgroundColor": "#f1f1f1", "textAlign": "center", "border": "1px solid #cbd5e0"}),
                ]))

            # Fila de Totales Generales (4 Columnas Exactas alineadas con el Header)
            filas_tabla.append(html.Tr([
                html.Td("TOTAL MATRÍCULA MUNICIPAL", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0"}),
                html.Td(f"{total_ninas_activos:,.0f}", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "backgroundColor": "#73243D", "textAlign": "center", "border": "1px solid #cbd5e0"}),
                html.Td(f"{total_ninos_activos:,.0f}", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "backgroundColor": "#73243D", "textAlign": "center", "border": "1px solid #cbd5e0"}),
                html.Td(f"{total_alumnos_unicos:,.0f}", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "backgroundColor": "#561B2E", "textAlign": "center", "border": "1px solid #cbd5e0"}),
            ]))

            tabla_layout = html.Div([
                html.Div("📋 DESGLOSE DE MATRÍCULA INSTITUCIONAL POR TALLER OPERATIVO", 
                         style={"padding": "9px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #cbd5e0", "fontSize": "11px", "color": "#4a5568"}),
                html.Div(
                    html.Table([
                        # Encabezado Principal: 4 columnas
                        html.Thead(html.Tr([
                            html.Th("Taller / Actividad Educativa", style={"fontSize": "10px", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0"}),
                            html.Th("👧 Niñas", style={"fontSize": "10px", "color": "#ffffff", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0", "textAlign": "center"}),
                            html.Th("👦 Niños", style={"fontSize": "10px", "color": "#ffffff", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0", "textAlign": "center"}),
                            html.Th("Total Inscritos", style={"fontSize": "10px", "color": "#ffffff", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#561B2E", "border": "1px solid #cbd5e0", "textAlign": "center"}),
                        ])),
                        html.Tbody(filas_tabla)
                    ], 
                    style={"width": "100%", "margin": "0", "borderCollapse": "collapse", "backgroundColor": "#ffffff"}
                    ),
                    style={"padding": "0px"}
                )
            ], style={"border": "1px solid #cbd5e0", "borderRadius": "6px", "marginTop": "16px", "backgroundColor": "#ffffff", "overflow": "hidden"})
        else:
            tabla_layout = html.Div()

        # =================================================================
        # 6. GRÁFICA INFERIOR: TENDENCIA HISTÓRICA MENSUAL
        # =================================================================
        if col_mes and col_variable:
            df_lineas = df_bib.groupby([col_mes, col_variable])[col_cantidad_sistema].sum().reset_index()
            df_lineas[col_mes] = pd.Categorical(df_lineas[col_mes], categories=orden_meses, ordered=True)
            df_lineas = df_lineas.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_lineas = pd.DataFrame()

        if not df_lineas.empty and df_lineas[col_cantidad_sistema].sum() > 0:
            fig_comparativa = px.line(
                df_lineas, x=col_mes, y=col_cantidad_sistema, color=col_variable, markers=True,
                color_discrete_map={"Niñas": "#b83280", "Niños": "#319795"},
                labels={col_cantidad_sistema: "Asistencias", col_mes: "", col_variable: "Segmento"}
            )
            fig_comparativa.update_layout(
                margin=dict(l=40, r=15, t=15, b=15),
                plot_bgcolor="white",
                height=240,
                yaxis={'gridcolor': '#f0f0f0'},
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            seccion_grafica = html.Div([
                html.Div("📈 COMPORTAMIENTO HISTÓRICO MENSUAL DE ASISTENCIA (FLUJO DE OPERACIÓN)", 
                         style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                dcc.Graph(figure=fig_comparativa, config={'displayModeBar': False})
            ], className="bg-white border shadow-sm mt-3", style={"borderRadius": "6px"})
        else:
            seccion_grafica = html.Div("ℹ️ No hay registros suficientes para estructurar el histórico.", style={"padding": "20px", "color": "#a0aec0", "fontSize": "12px"})

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            cuadrícula_kpis,   # Bloque superior 2x2
            tabla_layout,      # Tabla analítica simétrica de 4 columnas
            seccion_grafica    # Gráfica lineal histórica de control abajo
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Bibliotecas: {str(e)}", color="danger", className="m-3")
