# areas/secretaria_general.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_secretaria_general(df):
    """
    Módulo operativo para la Secretaría General.
    - Cuadrícula compacta de KPIs en 2x2.
    - Tabla nativa HTML purificada de 3 columnas (Simetría total sin fusiones para evitar bloqueos).
    - Identidad oficial de Morena (Guinda #73243D y Grises institucionales).
    - Gráfica comparativa mensual de la operación de Cabildo y Audiencias.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Secretaría General llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # LISTA DE ORDEN DE MESES GLOBAL
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # 1. Copiar y limpiar nombres de columnas
        df_sg = df.copy()
        df_sg.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_sg.columns]

        col_actividad = next((c for c in df_sg.columns if "ACTIVIDAD" in c), None)
        col_atendidos = next((c for c in df_sg.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_mes = next((c for c in df_sg.columns if "MES" in c), None)
        col_variable = next((c for c in df_sg.columns if "VARIABLE" in c), None)

        # 2. Conversión limpia de tipos de datos
        if col_atendidos:
            df_sg[col_atendidos] = pd.to_numeric(df_sg[col_atendidos], errors='coerce').fillna(0)
            col_cantidad_sistema = col_atendidos
        else:
            df_sg["CANTIDAD_GENERICA"] = 0
            col_cantidad_sistema = "CANTIDAD_GENERICA"

        if col_variable: df_sg[col_variable] = df_sg[col_variable].astype(str).str.strip().str.title()
        if col_actividad: df_sg[col_actividad] = df_sg[col_actividad].astype(str).str.strip().str.title()
        if col_mes: df_sg[col_mes] = df_sg[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. CÓMPUTO DE REGLAS DE NEGOCIO (KPIs)
        # =================================================================
        total_audiencias = df_sg[df_sg[col_actividad].str.contains("audiencia", case=False, na=False)][col_cantidad_sistema].sum()
        total_documentos = df_sg[df_sg[col_actividad].str.contains("constancia|documento", case=False, na=False)][col_cantidad_sistema].sum()
        total_cabildo = df_sg[df_sg[col_actividad].str.contains("cabildo", case=False, na=False)][col_cantidad_sistema].sum()
        total_gestiones = total_audiencias + total_documentos + total_cabildo

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
            html.Div("CUADRO DE MANDO - SECRETARÍA GENERAL MUNICIPAL", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#73243D", "marginBottom": "12px", "letterSpacing": "0.8px"}),
            
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("🗣️ AUDIENCIAS CON LA CIUDADANÍA", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_audiencias:,.0f} atendidas", style={"margin": "2px 0", "fontWeight": "700", "color": "#2b6cb0", "fontSize": "18px"}),
                    html.Div("Atención directa del Secretario", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("📄 CONSTANCIAS Y TRÁMITES", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_documentos:,.0f} emitidas", style={"margin": "2px 0", "fontWeight": "700", "color": "#319795", "fontSize": "18px"}),
                    html.Div("Certeza jurídica e identidad", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),
            ], className="g-2"),

            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("🏛️ SESIONES DE CABILDO EFECTUADAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_cabildo:,.0f} sesiones", style={"margin": "2px 0", "fontWeight": "700", "color": "#b83280", "fontSize": "18px"}),
                    html.Div("Ordinarias y Extraordinarias", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("⚡ TOTAL GESTIONES ADMINISTRATIVAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{total_gestiones:,.0f} acciones", style={"margin": "2px 0", "fontWeight": "700", "color": "#4a5568", "fontSize": "18px"}),
                    html.Div("Impacto operativo total en el área", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),
            ], className="g-2")
        ])

        # =================================================================
        # 5. CONSTRUCCIÓN DE LA TABLA (3 COLUMNAS COMPLETAMENTE INDEPENDIENTES)
        # =================================================================
        df_resumen = df_sg.groupby([col_actividad, col_variable])[col_cantidad_sistema].sum().reset_index()
        df_resumen = df_resumen.sort_values(by=col_cantidad_sistema, ascending=False)

        filas_tabla = []
        for _, r in df_resumen.iterrows():
            filas_tabla.append(html.Tr([
                # Columna 1: Actividad
                html.Td(r[col_actividad], style={"fontSize": "11px", "color": "#2d3748", "textAlign": "left", "padding": "8px 14px", "fontWeight": "500", "backgroundColor": "#f9f9f9", "border": "1px solid #cbd5e0"}),
                # Columna 2: Eje u Operación
                html.Td(r[col_variable], style={"fontSize": "11px", "color": "#4a5568", "padding": "8px 14px", "backgroundColor": "#ffffff", "textAlign": "left", "border": "1px solid #cbd5e0"}),
                # Columna 3: Total Anual Atendidos
                html.Td(f"{r[col_cantidad_sistema]:,.0f}", style={"fontSize": "11px", "color": "#1a202c", "fontWeight": "700", "padding": "8px 14px", "backgroundColor": "#f1f1f1", "textAlign": "center", "border": "1px solid #cbd5e0"}),
            ]))

        # Fila de Totales Generales (3 celdas individuales separadas para asegurar simetría total)
        filas_tabla.append(html.Tr([
            html.Td("TOTAL DE ATENCIONES Y GESTIONES GENERALES", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0"}),
            html.Td("Consolidado Anual del Área", style={"fontSize": "11px", "fontWeight": "600", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0"}),
            html.Td(f"{total_gestiones:,.0f}", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "backgroundColor": "#561B2E", "textAlign": "center", "border": "1px solid #cbd5e0"}),
        ]))

        tabla_layout = html.Div([
            html.Div("📋 BALANCE ANUAL DE INDICADORES EN SECRETARÍA GENERAL", 
                     style={"padding": "9px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #cbd5e0", "fontSize": "11px", "color": "#4a5568"}),
            html.Div(
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Actividad Registrada", style={"fontSize": "10px", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0", "width": "50%"}),
                        html.Th("Eje Operativo / Clasificación", style={"fontSize": "10px", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0", "width": "35%"}),
                        html.Th("Total Absoluto", style={"fontSize": "10px", "color": "#ffffff", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#561B2E", "border": "1px solid #cbd5e0", "textAlign": "center", "width": "15%"}),
                    ])),
                    html.Tbody(filas_tabla)
                ], 
                style={"width": "100%", "margin": "0", "borderCollapse": "collapse", "backgroundColor": "#ffffff"}
                ),
                style={"padding": "0px"}
            )
        ], style={"border": "1px solid #cbd5e0", "borderRadius": "6px", "marginTop": "16px", "backgroundColor": "#ffffff", "overflow": "hidden"})

        # =================================================================
        # 6. GRÁFICA INFERIOR: FLUJO MENSUAL DE ACTIVIDADES
        # =================================================================
        if col_mes and col_variable:
            df_lineas = df_sg.groupby([col_mes, col_variable])[col_cantidad_sistema].sum().reset_index()
            df_lineas[col_mes] = pd.Categorical(df_lineas[col_mes], categories=orden_meses, ordered=True)
            df_lineas = df_lineas.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_lineas = pd.DataFrame()

        if not df_lineas.empty and df_lineas[col_cantidad_sistema].sum() > 0:
            fig_comparativa = px.bar(
                df_lineas, x=col_mes, y=col_cantidad_sistema, color=col_variable,
                barmode="group",
                color_discrete_map={
                    "Atención Personal A La Población": "#2b6cb0",
                    "Actividades Administrativas": "#319795",
                    "Sesiones De Cabildo": "#b83280"
                },
                labels={col_cantidad_sistema: "Volumen", col_mes: "", col_variable: "Clasificación"}
            )
            fig_comparativa.update_layout(
                margin=dict(l=40, r=15, t=15, b=15),
                plot_bgcolor="white",
                height=250,
                yaxis={'gridcolor': '#f0f0f0'},
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            seccion_grafica = html.Div([
                html.Div("📈 DINÁMICA DE TRABAJO MENSUAL (DISTRIBUCIÓN DE CARGA OPERATIVA)", 
                         style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                dcc.Graph(figure=fig_comparativa, config={'displayModeBar': False})
            ], className="bg-white border shadow-sm mt-3", style={"borderRadius": "6px"})
        else:
            seccion_grafica = html.Div("ℹ️ No hay registros suficientes para estructurar el histórico.", style={"padding": "20px", "color": "#a0aec0", "fontSize": "12px"})

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            cuadrícula_kpis,   
            tabla_layout,      
            seccion_grafica    
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Secretaría General: {str(e)}", color="danger", className="m-3")
