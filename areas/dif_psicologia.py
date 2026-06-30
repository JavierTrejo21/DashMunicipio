# areas/dif_psicologia.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_dif_psicologia(df):
    """
    Módulo híbrido de Alto Impacto para DIF Psicología.
    - Panel Izquierdo: Tabla de resumen demográfico simple, limpia y ordenada.
    - Panel Derecho: Embudo visual (Funnel Chart) de problemáticas clínicas.
    - Sin desglose de meses innecesarios para un análisis ejecutivo directo.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de DIF Psicología llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_psic = df.copy()
        df_psic.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_psic.columns]

        col_actividad = next((c for c in df_psic.columns if "ACTIVIDAD" in c), None)
        col_atendidos = next((c for c in df_psic.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_variable = next((c for c in df_psic.columns if "VARIABLE" in c), None)

        # Conversión de tipos de datos
        if col_atendidos:
            df_psic[col_atendidos] = pd.to_numeric(df_psic[col_atendidos], errors='coerce').fillna(0)
            col_cantidad_sistema = col_atendidos
        else:
            df_psic["CANTIDAD_GENERICA"] = 0
            col_cantidad_sistema = "CANTIDAD_GENERICA"

        if col_variable: df_psic[col_variable] = df_psic[col_variable].astype(str).str.strip().str.title()
        if col_actividad: df_psic[col_actividad] = df_psic[col_actividad].astype(str).str.strip().str.title()

        # Separación por bloques operativos (Anualizado sin meses)
        df_temas = df_psic[df_psic[col_variable].str.contains("Tema|Trastorno", case=False, na=False)]
        df_demo = df_psic[df_psic[col_variable].str.contains("Demografica|Paciente", case=False, na=False)]

        # =================================================================
        # 2. CÓMPUTO DE REGLAS DE NEGOCIO (KPIs)
        # =================================================================
        total_consultas = df_temas[col_cantidad_sistema].sum()
        total_pacientes = df_demo[col_cantidad_sistema].sum()
        
        df_top_trastorno = df_temas.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        if not df_top_trastorno.empty:
            top_row = df_top_trastorno.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0]
            top_incidencia = f"{top_row[col_actividad]}"
        else:
            top_incidencia = "N/A"

        # Estilo de las tarjetas de control superiores
        estilo_tarjeta = {
            "borderRadius": "6px",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.04)",
            "border": "1px solid #eef2f5",
            "backgroundColor": "#ffffff",
            "padding": "12px 14px",
            "textAlign": "center",
            "height": "100%"
        }

        seccion_kpis = dbc.Row([
            dbc.Col(html.Div([
                html.Div("🧠 TOTAL CONSULTAS CLÍNICAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(f"{total_consultas:,.0f} sesiones", style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#73243D", "fontSize": "20px"})
            ], style=estilo_tarjeta), width=12, sm=4),
            
            dbc.Col(html.Div([
                html.Div("👥 CIUDADANOS ATENDIDOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(f"{total_pacientes:,.0f} personas", style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#2b6cb0", "fontSize": "20px"})
            ], style=estilo_tarjeta), width=12, sm=4),
            
            dbc.Col(html.Div([
                html.Div("🚨 PRINCIPAL DIAGNÓSTICO", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(top_incidencia, style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#e53e3e", "fontSize": "14px", "lineHeight": "22px"})
            ], style=estilo_tarjeta), width=12, sm=4),
        ], className="g-2 mb-3")

        # =================================================================
        # 3. PANEL IZQUIERDO: TABLA DE RESUMEN DEMOGRÁFICO SENCILLA
        # =================================================================
        df_demo_agrupado = df_demo.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_demo_agrupado = df_demo_agrupado.sort_values(by=col_cantidad_sistema, ascending=False)

        filas_tabla_demo = []
        for _, r in df_demo_agrupado.iterrows():
            filas_tabla_demo.append(html.Tr([
                html.Td(r[col_actividad], style={"fontSize": "11px", "color": "#2d3748", "textAlign": "left", "padding": "10px 14px", "fontWeight": "500", "backgroundColor": "#f9f9f9", "border": "1px solid #cbd5e0"}),
                html.Td(f"{r[col_cantidad_sistema]:,.0f}", style={"fontSize": "11px", "color": "#1a202c", "fontWeight": "700", "padding": "10px 14px", "backgroundColor": "#ffffff", "textAlign": "center", "border": "1px solid #cbd5e0"}),
            ]))

        # Fila de Cierre para el total demográfico
        filas_tabla_demo.append(html.Tr([
            html.Td("TOTAL PACIENTES ÚNICOS", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0"}),
            html.Td(f"{total_pacientes:,.0f}", style={"fontSize": "11px", "fontWeight": "700", "color": "#ffffff", "backgroundColor": "#561B2E", "textAlign": "center", "border": "1px solid #cbd5e0"}),
        ]))

        tabla_layout_sencilla = html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Grupo Vulnerable / Edad y Género", style={"fontSize": "10px", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#73243D", "border": "1px solid #cbd5e0", "width": "75%"}),
                    html.Th("Total", style={"fontSize": "10px", "color": "#ffffff", "padding": "10px 14px", "fontWeight": "600", "backgroundColor": "#561B2E", "border": "1px solid #cbd5e0", "textAlign": "center", "width": "25%"}),
                ])),
                html.Tbody(filas_tabla_demo)
            ], 
            style={"width": "100%", "margin": "0", "borderCollapse": "collapse", "backgroundColor": "#ffffff"}
            )
        ], style={"border": "1px solid #cbd5e0", "borderRadius": "6px", "overflow": "hidden"})

        # =================================================================
        # 4. PANEL DERECHO: EMBUDO (FUNNEL) DE INCIDENCIAS CLÍNICAS
        # =================================================================
        df_temas_agrupado = df_temas.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_temas_agrupado = df_temas_agrupado.sort_values(by=col_cantidad_sistema, ascending=False)

        fig_embudo = px.funnel(
            df_temas_agrupado, x=col_cantidad_sistema, y=col_actividad,
            color_discrete_sequence=["#319795"],
            labels={col_cantidad_sistema: "Casos", col_actividad: "Diagnóstico"}
        )
        fig_embudo.update_layout(
            margin=dict(l=10, r=20, t=10, b=10),
            plot_bgcolor="white",
            height=320,
            font=dict(size=11)
        )
        fig_embudo.update_yaxes(automargin=True)

        # =================================================================
        # 5. INTEGRACIÓN DEL LAYOUT BILATERAL (TABLA + EMBUDO)
        # =================================================================
        bloque_dashboard = dbc.Row([
            # Columna de la Tabla Resumen (Izquierda)
            dbc.Col(html.Div([
                html.Div("📋 RESUMEN DE MATRÍCULA Y PERFIL DE PACIENTES", 
                         style={"padding": "10px 14px", "fontWeight": "700", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568", "letterSpacing": "0.3px"}),
                html.Div(tabla_layout_sencilla, style={"padding": "12px"})
            ], className="bg-white border shadow-sm", style={"borderRadius": "6px", "height": "100%"}), width=12, lg=5),

            # Columna del Embudo Premium (Derecha)
            dbc.Col(html.Div([
                html.Div("🔻 EMBUDO DE PROBLEMÁTICAS Y SALUD MENTAL DETECTADA", 
                         style={"padding": "10px 14px", "fontWeight": "700", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568", "letterSpacing": "0.3px"}),
                html.Div(dcc.Graph(figure=fig_embudo, config={'displayModeBar': False}), style={"padding": "5px"})
            ], className="bg-white border shadow-sm", style={"borderRadius": "6px", "height": "100%"}), width=12, lg=7),
        ], className="g-3")

        return html.Div([
            html.Div("DIAGNÓSTICO INSTITUCIONAL - DEPARTAMENTO DE PSICOLOGÍA", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#73243D", "marginBottom": "14px", "letterSpacing": "0.8px"}),
            seccion_kpis,
            bloque_dashboard
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error en la consolidación del módulo híbrido de DIF Psicología: {str(e)}", color="danger", className="m-3")
