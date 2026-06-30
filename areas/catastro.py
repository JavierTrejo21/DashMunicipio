# areas/catastro.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_catastro(df):
    """
    Módulo operativo para Catastro Municipal.
    Presenta KPIs clave y un desglose visual corregido para nombres largos en ejes.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Catastro llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_cat = df.copy()
        df_cat.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_cat.columns]

        # Mapear columnas dinámicamente
        col_mes = next((c for c in df_cat.columns if "MES" in c), None)
        col_atendidos = next((c for c in df_cat.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_cat.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_cat.columns if "VARIABLE" in c), None)

        # 2. Conversión limpia de tipos de datos y estandarización de texto
        if col_atendidos:
            df_cat[col_atendidos] = pd.to_numeric(df_cat[col_atendidos], errors='coerce').fillna(0)
        
        if col_variable: df_cat[col_variable] = df_cat[col_variable].astype(str).str.strip()
        if col_actividad: df_cat[col_actividad] = df_cat[col_actividad].astype(str).str.strip()
        
        if col_mes:
            df_cat[col_mes] = df_cat[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. EXTRACCIÓN DE MÉTRICAS OPERATIVAS
        # =================================================================
        total_tramites = df_cat[col_atendidos].sum() if col_atendidos else 0
        
        df_constancias = df_cat[df_cat[col_variable].str.contains("constancia", case=False, na=False)] if col_variable else pd.DataFrame()
        total_constancias = df_constancias[col_atendidos].sum() if not df_constancias.empty and col_atendidos else 0

        df_tecnicos = df_cat[df_cat[col_variable].str.contains("actualiz|tecnica|modific", case=False, na=False)] if col_variable else pd.DataFrame()
        total_tecnicos = df_tecnicos[col_atendidos].sum() if not df_tecnicos.empty and col_atendidos else 0

        if col_actividad and col_atendidos and not df_cat.empty:
            df_top_act = df_cat.groupby(col_actividad)[col_atendidos].sum().reset_index()
            if not df_top_act.empty and df_top_act[col_atendidos].sum() > 0:
                top_tramite_row = df_top_act.sort_values(by=col_atendidos, ascending=False).iloc[0]
                top_tramite_nombre = str(top_tramite_row[col_actividad])
                if len(top_tramite_nombre) > 25: top_tramite_nombre = top_tramite_nombre[:22] + "..."
            else:
                top_tramite_nombre = "Sin registros"
        else:
            top_tramite_nombre = "No disponible"

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
            html.Div("CONTROL OPERATIVO DE CATASTRO MUNICIPAL", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#691c32", "marginBottom": "10px", "letterSpacing": "0.8px"}),
            
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("📋 TRÁMITES TOTALES", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_tramites:,.0f} servicios", style={"margin": "2px 0", "fontWeight": "700", "color": "#2b6cb0", "fontSize": "18px"}),
                    html.Div("Flujo acumulado del periodo", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("📄 CONSTANCIAS EMITIDAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_constancias:,.0f} docs.", style={"margin": "2px 0", "fontWeight": "700", "color": "#2f855a", "fontSize": "18px"}),
                    html.Div("No adeudos, posesión y valor", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("📐 MODIFICACIONES TÉCNICAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_tecnicos:,.0f} actos", style={"margin": "2px 0", "fontWeight": "700", "color": "#691c32", "fontSize": "18px"}),
                    html.Div("Traslados, avalúos y deslindes", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("🌟 MAYOR OPERATIVIDAD EN", style={"fontSize": "9px", "fontWeight": "700", "color": "#4a5568", "textTransform": "uppercase"}),
                    html.H4(top_tramite_nombre, style={"margin": "2px 0", "fontWeight": "700", "color": "#4a5568", "fontSize": "13px", "lineHeight": "22px"}),
                    html.Div("Trámite con mayor volumen", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),
            ], className="g-2")
        ])

        # =================================================================
        # 5. CONFIGURACIÓN DE GRÁFICAS SEGURAS
        # =================================================================
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Gráfica Mensual (Línea)
        if col_mes and col_atendidos:
            df_mes = df_cat.groupby(col_mes)[col_atendidos].sum().reset_index()
            df_mes[col_mes] = pd.Categorical(df_mes[col_mes], categories=orden_meses, ordered=True)
            df_mes = df_mes.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_mes = pd.DataFrame()

        if not df_mes.empty and df_mes[col_atendidos].sum() > 0:
            fig_mensual = px.line(
                df_mes, x=col_mes, y=col_atendidos, markers=True,
                color_discrete_sequence=["#2b6cb0"],
                labels={col_atendidos: "Cantidad de Trámites", col_mes: ""}
            )
            fig_mensual.update_layout(margin=dict(l=40, r=15, t=15, b=15), plot_bgcolor="white", height=260, yaxis={'gridcolor': '#f0f0f0'})
            graph_left = dcc.Graph(figure=fig_mensual, config={'displayModeBar': False})
        else:
            graph_left = html.Div("ℹ️ No hay datos suficientes para graficar la tendencia mensual.", style={"padding": "40px 20px", "textAlign": "center", "color": "#a0aec0", "fontSize": "12px"})

        # Gráfica Top Actividades (Barras Horizontales con Ajuste de Margen Amplio)
        if col_actividad and col_atendidos:
            df_top5 = df_cat.groupby(col_actividad)[col_atendidos].sum().reset_index()
            df_top5 = df_top5[df_top5[col_atendidos] > 0].sort_values(by=col_atendidos, ascending=True).tail(5)
        else:
            df_top5 = pd.DataFrame()

        if not df_top5.empty:
            fig_actividades = px.bar(
                df_top5, x=col_atendidos, y=col_actividad, orientation='h',
                color_discrete_sequence=["#691c32"],
                labels={col_atendidos: "Total Atendidos", col_actividad: ""}
            )
            
            # Dejamos que Plotly muestre el nombre completo (quitamos el recorte de texto)
            fig_actividades.update_yaxes(
                tickvals=df_top5[col_actividad], 
                tickfont=dict(size=9)  # Ajustamos levemente el tamaño para que encaje perfecto
            )
            
            # CAMBIO CLAVE: Ampliamos el margen izquierdo a 230 para dar espacio a los textos completos
            fig_actividades.update_layout(
                margin=dict(l=230, r=15, t=15, b=15), 
                plot_bgcolor="white", 
                height=260, 
                xaxis={'gridcolor': '#f0f0f0'}
            )
            graph_right = dcc.Graph(figure=fig_actividades, config={'displayModeBar': False})
        else:
            graph_right = html.Div("ℹ️ No hay registros operativos válidos para desglosar el Top de Trámites.", style={"padding": "40px 20px", "textAlign": "center", "color": "#a0aec0", "fontSize": "12px"})

        # =================================================================
        # 6. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            tarjetas_variables,  
            html.Hr(style={"margin": "15px 0", "opacity": "0.1"}),
            
            dbc.Row([
                # Panel Izquierdo: Comportamiento por Meses
                dbc.Col(html.Div([
                    html.Div("📈 DEMANDA DE ATENCIÓN CATASTRAL POR MES", style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                    graph_left
                ], className="bg-white border shadow-sm", style={"borderRadius": "6px"}), md=6, className="mb-2"),

                # Panel Derecho: Top Trámites Solicitados
                dbc.Col(html.Div([
                    html.Div("🎯 TOP 5 TRÁMITES CON MAYOR AFLUENCIA CIUDADANA", style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                    graph_right
                ], className="bg-white border shadow-sm", style={"borderRadius": "6px"}), md=6, className="mb-2")
            ])
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Catastro: {str(e)}", color="danger", className="m-3")
