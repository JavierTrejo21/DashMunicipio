# areas/proteccion_civil.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_proteccion_civil(df):
    """
    Módulo operativo para Protección Civil.
    Analiza el flujo de emergencias, riesgos meteorológicos e impacto por comunidades.
    Corrección aplicada: Evita la duplicidad de datos en las tarjetas de resumen.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Protección Civil llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_pc = df.copy()
        df_pc.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_pc.columns]

        # Identificación dinámica de columnas
        col_mes = next((c for c in df_pc.columns if "MES" in c), None)
        col_atendidos = next((c for c in df_pc.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_pc.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_pc.columns if "VARIABLE" in c), None)
        col_comunidad = next((c for c in df_pc.columns if "COMUNIDAD" in c or "LOCALIDAD" in c), None)

        # 2. Conversión limpia de datos y estandarización
        if col_atendidos:
            df_pc[col_atendidos] = pd.to_numeric(df_pc[col_atendidos], errors='coerce').fillna(0)
            # Homologación global del sistema por si algún callback externo busca 'CANTIDAD'
            df_pc["CANTIDAD"] = df_pc[col_atendidos]
            col_cantidad_sistema = "CANTIDAD"
        else:
            df_pc["CANTIDAD"] = 0
            col_cantidad_sistema = "CANTIDAD"

        if col_variable: df_pc[col_variable] = df_pc[col_variable].astype(str).str.strip()
        if col_actividad: df_pc[col_actividad] = df_pc[col_actividad].astype(str).str.strip()
        if col_comunidad: df_pc[col_comunidad] = df_pc[col_comunidad].astype(str).str.strip().str.upper()
        if col_mes: df_pc[col_mes] = df_pc[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. EXTRACCIÓN DE MÉTRICAS OPERATIVAS (FILTROS EXCLUSIVOS)
        # =================================================================
        total_emergencias = df_pc[col_cantidad_sistema].sum()

        # 'meteor|clima|riesgo' atrapa "Atención a Riesgos Meteorológicos"
        df_meteorologicos = df_pc[df_pc[col_variable].str.contains("meteor|clima|riesgo", case=False, na=False)] if col_variable else pd.DataFrame()
        total_meteorologicos = df_meteorologicos[col_cantidad_sistema].sum() if not df_meteorologicos.empty else 0

        # SOLUCIÓN DE DUPLICIDAD: Al buscar solo por 'poblac' aislamos "Atención a la Población" de forma única
        df_poblacion = df_pc[df_pc[col_variable].str.contains("poblac", case=False, na=False)] if col_variable else pd.DataFrame()
        total_poblacion = df_poblacion[col_cantidad_sistema].sum() if not df_poblacion.empty else 0

        # Obtener la comunidad con mayor incidencia
        if col_comunidad and not df_pc.empty:
            df_top_com = df_pc.groupby(col_comunidad)[col_cantidad_sistema].sum().reset_index()
            # Filtrar posibles registros vacíos o guiones de formato
            df_top_com = df_top_com[~df_top_com[col_comunidad].str.contains("UNKNOWN|VACIO|-|S/N", na=False)]
            if not df_top_com.empty and df_top_com[col_cantidad_sistema].sum() > 0:
                top_com_row = df_top_com.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0]
                top_comunidad_nombre = str(top_com_row[col_comunidad]).title()
                if len(top_comunidad_nombre) > 22: top_comunidad_nombre = top_comunidad_nombre[:19] + "..."
            else:
                top_comunidad_nombre = "Sin registros"
        else:
            top_comunidad_nombre = "No disponible"

        # =================================================================
        # 4. DISEÑO DE TARJETAS DE RESUMEN INDEPENDIENTES
        # =================================================================
        estilo_tarjeta = {
            "borderRadius": "6px",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
            "border": "1px solid #eef2f5",
            "backgroundColor": "#ffffff",
            "padding": "10px 14px",
            "height": "100%"
        }

        tarjetas_variables = html.Div([
            html.Div("CUADRO DE MANDO - PROTECCIÓN CIVIL Y BOMBEROS", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#691c32", "marginBottom": "10px", "letterSpacing": "0.8px"}),
            
            dbc.Row([
                # Card 1: Total Servicios Absolutos
                dbc.Col(html.Div([
                    html.Div("🚨 EMERGENCIAS ATENDIDAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_emergencias:,.0f} servicios", style={"margin": "2px 0", "fontWeight": "700", "color": "#c53030", "fontSize": "18px"}),
                    html.Div("Total de auxilios en el municipio", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),

                # Card 2: Riesgos Meteorológicos
                dbc.Col(html.Div([
                    html.Div("🌧️ RIESGOS METEOROLÓGICOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_meteorologicos:,.0f} eventos", style={"margin": "2px 0", "fontWeight": "700", "color": "#2b6cb0", "fontSize": "18px"}),
                    html.Div("Derrumbes, deslaves y afectaciones", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),

                # Card 3: Atención Directa Población (NETO DESACOPLADO)
                dbc.Col(html.Div([
                    html.Div("👥 ATENCIÓN A LA POBLACIÓN", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_poblacion:,.0f} auxilios", style={"margin": "2px 0", "fontWeight": "700", "color": "#2f855a", "fontSize": "18px"}),
                    html.Div("Incendios, rescates y salvamientos", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),

                # Card 4: Comunidad Crítica
                dbc.Col(html.Div([
                    html.Div("📍 ZONA DE MAYOR IMPACTO", style={"fontSize": "9px", "fontWeight": "700", "color": "#4a5568", "textTransform": "uppercase"}),
                    html.H4(top_comunidad_nombre, style={"margin": "2px 0", "fontWeight": "700", "color": "#4a5568", "fontSize": "14px", "lineHeight": "22px"}),
                    html.Div("Localidad con más incidencias", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),
            ], className="g-2")
        ])

        # =================================================================
        # 5. CONFIGURACIÓN DE GRÁFICAS (Comportamiento Mensual e Impacto Local)
        # =================================================================
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Gráfica Temporal Mensual
        if col_mes:
            df_mes = df_pc.groupby(col_mes)[col_cantidad_sistema].sum().reset_index()
            df_mes[col_mes] = pd.Categorical(df_mes[col_mes], categories=orden_meses, ordered=True)
            df_mes = df_mes.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_mes = pd.DataFrame()

        if not df_mes.empty and df_mes[col_cantidad_sistema].sum() > 0:
            fig_mensual = px.line(
                df_mes, x=col_mes, y=col_cantidad_sistema, markers=True,
                color_discrete_sequence=["#c53030"], 
                labels={col_cantidad_sistema: "Incidencias Atendidas", col_mes: ""}
            )
            fig_mensual.update_layout(margin=dict(l=40, r=15, t=15, b=15), plot_bgcolor="white", height=260, yaxis={'gridcolor': '#f0f0f0'})
            graph_left = dcc.Graph(figure=fig_mensual, config={'displayModeBar': False})
        else:
            graph_left = html.Div("ℹ️ No hay datos suficientes para graficar la tendencia temporal.", style={"padding": "40px 20px", "textAlign": "center", "color": "#a0aec0", "fontSize": "12px"})

        # Gráfica de Impacto Territorial por Comunidad (Top 5)
        if col_comunidad:
            df_com5 = df_pc.groupby(col_comunidad)[col_cantidad_sistema].sum().reset_index()
            df_com5 = df_com5[df_com5[col_cantidad_sistema] > 0].sort_values(by=col_cantidad_sistema, ascending=True).tail(5)
            df_com5[col_comunidad] = df_com5[col_comunidad].str.title()
        else:
            df_com5 = pd.DataFrame()

        if not df_com5.empty:
            fig_comunidades = px.bar(
                df_com5, x=col_cantidad_sistema, y=col_comunidad, orientation='h',
                color_discrete_sequence=["#691c32"],
                labels={col_cantidad_sistema: "Total Reportes", col_comunidad: ""}
            )
            fig_comunidades.update_yaxes(tickvals=df_com5[col_comunidad], tickfont=dict(size=9))
            fig_comunidades.update_layout(margin=dict(l=180, r=15, t=15, b=15), plot_bgcolor="white", height=260, xaxis={'gridcolor': '#f0f0f0'}
            )
            graph_right = dcc.Graph(figure=fig_comunidades, config={'displayModeBar': False})
        else:
            graph_right = html.Div("ℹ️ No hay registros válidos para desglosar el impacto por comunidad.", style={"padding": "40px 20px", "textAlign": "center", "color": "#a0aec0", "fontSize": "12px"})

        # =================================================================
        # 6. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            tarjetas_variables,  
            html.Hr(style={"margin": "15px 0", "opacity": "0.1"}),
            
            dbc.Row([
                # Panel Izquierdo: Comportamiento Temporal
                dbc.Col(html.Div([
                    html.Div("📈 HISTÓRICO DE INCIDENCIAS MENSUALES", style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                    graph_left
                ], className="bg-white border shadow-sm", style={"borderRadius": "6px"}), md=6, className="mb-2"),

                # Panel Derecho: Distribución Territorial
                dbc.Col(html.Div([
                    html.Div("🎯 TOP 5 COMUNIDADES CON MAYOR NÚMERO DE AUXILIOS", style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                    graph_right
                ], className="bg-white border shadow-sm", style={"borderRadius": "6px"}), md=6, className="mb-2")
            ])
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Protección Civil: {str(e)}", color="danger", className="m-3")
