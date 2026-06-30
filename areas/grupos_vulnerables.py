# areas/grupos_vulnerables.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_grupos_vulnerables(df):
    """
    Módulo Operativo Simplificado para Grupos Vulnerables.
    - Centrado exclusivamente en la cantidad de beneficiarios (Sin datos financieros).
    - Remueve de forma automática las comunidades con valores en cero.
    - Dos gráficas limpias y balanceadas de personas atendidas.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Grupos Vulnerables llegó vacío.", color="warning", className="m-3")

    try:
        # 1. Limpieza y normalización estándar de columnas
        df_vuel = df.copy()
        df_vuel.columns = [str(c).strip().upper() for c in df_vuel.columns]

        col_comunidad = next((c for c in df_vuel.columns if "COMUNIDAD" in c), None)
        col_beneficiarios = next((c for c in df_vuel.columns if "BENEFICIARIO" in c or "CANTIDAD" in c), None)
        col_programa = next((c for c in df_vuel.columns if "PROGRAMA" in c), None)

        if col_beneficiarios: 
            df_vuel[col_beneficiarios] = pd.to_numeric(df_vuel[col_beneficiarios], errors='coerce').fillna(0)
            col_cantidad_sistema = col_beneficiarios
        else:
            df_vuel["BENEFICIARIOS_GENERICO"] = 0
            col_cantidad_sistema = "BENEFICIARIOS_GENERICO"

        if col_programa: df_vuel[col_programa] = df_vuel[col_programa].astype(str).str.strip()

        # 🔥 CLAVE DE LA SIMPLICIDAD: Quedarse únicamente con registros que sí tienen beneficiarios
        df_activos = df_vuel[df_vuel[col_cantidad_sistema] > 0].copy()

        # =================================================================
        # 2. MÉTRICAS SUPERIORES DE CONTROL (KPIs)
        # =================================================================
        total_beneficiarios = df_activos[col_cantidad_sistema].sum()
        total_comunidades = df_activos[col_comunidad].nunique()

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
                html.Div("👥 TOTAL CIUDADANOS ATENDIDOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(f"{total_beneficiarios:,.0f} personas", style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#73243D", "fontSize": "20px"})
            ], style=estilo_tarjeta), width=12, sm=6),
            
            dbc.Col(html.Div([
                html.Div("📍 LOCALIDADES CON COBERTURA ACTIVA", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(f"{total_comunidades} Comunidades", style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#2b6cb0", "fontSize": "20px"})
            ], style=estilo_tarjeta), width=12, sm=6),
        ], className="g-2 mb-3")

        # =================================================================
        # 3. GRÁFICA 1: PERSONAS ATENDIDAS POR LOCALIDAD (Izquierda)
        # =================================================================
        df_geo = df_activos.groupby(col_comunidad)[col_cantidad_sistema].sum().reset_index()
        df_geo = df_geo.sort_values(by=col_cantidad_sistema, ascending=True)

        fig_comunidades = px.bar(
            df_geo, x=col_cantidad_sistema, y=col_comunidad, orientation='h',
            color_discrete_sequence=["#2b6cb0"],
            labels={col_cantidad_sistema: "Beneficiarios", col_comunidad: ""}
        )
        fig_comunidades.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white",
            height=280,
            xaxis={'gridcolor': '#f0f0f0'}
        )
        fig_comunidades.update_yaxes(automargin=True)

        # =================================================================
        # 4. GRÁFICA 2: PERSONAS ATENDIDAS POR TIPO DE PROGRAMA (Derecha)
        # =================================================================
        df_prog = df_activos.groupby(col_programa)[col_cantidad_sistema].sum().reset_index()

        fig_programas = px.bar(
            df_prog, x=col_programa, y=col_cantidad_sistema,
            color_discrete_sequence=["#319795"],
            labels={col_cantidad_sistema: "Ciudadanos Atendidos", col_programa: ""}
        )
        fig_programas.update_layout(
            margin=dict(l=10, r=10, t=15, b=10),
            plot_bgcolor="white",
            height=280,
            yaxis={'gridcolor': '#f0f0f0'}
        )
        fig_programas.update_xaxes(automargin=True)

        # =================================================================
        # 5. DISPOSICIÓN DUAL EN PANTALLA
        # =================================================================
        bloque_dashboard = dbc.Row([
            # Izquierda: Comunidades sin ceros
            dbc.Col(html.Div([
                html.Div("📍 DISTRIBUCIÓN DE POBLACIÓN ATENDIDA POR COMUNIDAD", 
                         style={"padding": "10px 14px", "fontWeight": "700", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                html.Div(dcc.Graph(figure=fig_comunidades, config={'displayModeBar': False}), style={"padding": "5px"})
            ], className="bg-white border shadow-sm", style={"borderRadius": "6px", "height": "100%"}), width=12, lg=6),

            # Derecha: Programas
            dbc.Col(html.Div([
                html.Div("🎯 POBLACIÓN BENEFICIADA POR TIPO DE PROGRAMA", 
                         style={"padding": "10px 14px", "fontWeight": "700", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                html.Div(dcc.Graph(figure=fig_programas, config={'displayModeBar': False}), style={"padding": "5px"})
            ], className="bg-white border shadow-sm", style={"borderRadius": "6px", "height": "100%"}), width=12, lg=6),
        ], className="g-3")

        return html.Div([
            html.Div("EVALUACIÓN DE IMPACTO SOCIAL - ATENCIÓN A GRUPOS VULNERABLES", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#73243D", "marginBottom": "14px", "letterSpacing": "0.8px"}),
            seccion_kpis,
            bloque_dashboard
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el módulo simplificado: {str(e)}", color="danger", className="m-3")
