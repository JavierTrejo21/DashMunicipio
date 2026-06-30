# areas/ecologia.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

def analizar_ecologia(df):
    """
    Módulo operativo y financiero para Ecología y Medio Ambiente.
    Filtra estrictamente por 'Proyectos Reelevantes' para la tabla inferior,
    dejando 'Proyectos Ecologicos Implementados' y el resto en los KPIs/Gráficas.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Ecología llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_eco = df.copy()
        df_eco.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_eco.columns]

        col_mes = next((c for c in df_eco.columns if "MES" in c), None)
        col_cantidad = next((c for c in df_eco.columns if "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_eco.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_eco.columns if "VARIABLE" in c), None)
        col_ingresos = next((c for c in df_eco.columns if "INGRESO" in c), None)
        col_beneficiarios = next((c for c in df_eco.columns if "BENEFICIARIO" in c), None)
        col_inversion = next((c for c in df_eco.columns if "INVERSION" in c), None)

        # 2. Conversión limpia a tipos numéricos y texto
        for col in [col_cantidad, col_ingresos, col_beneficiarios, col_inversion]:
            if col:
                df_eco[col] = pd.to_numeric(df_eco[col], errors='coerce').fillna(0)
        
        if col_variable: df_eco[col_variable] = df_eco[col_variable].astype(str).str.strip()
        if col_actividad: df_eco[col_actividad] = df_eco[col_actividad].astype(str).str.strip()

        # =================================================================
        # FILTRO ESTRICTO: Separar únicamente "Proyectos Reelevantes"
        # =================================================================
        # Buscamos la coincidencia exacta ignorando mayúsculas/minúsculas y espacios basura
        if col_variable:
            mask_proyectos = df_eco[col_variable].str.lower() == "proyectos reelevantes"
        else:
            mask_proyectos = pd.Series(False, index=df_eco.index)
        
        # DataFrame único para la tabla inferior (Contiene las descripciones reales)
        df_proyectos_raw = df_eco[mask_proyectos].copy()
        
        # DataFrame que alimenta las tarjetas y gráficas (Mantiene 'Proyectos Ecologicos Implementados')
        df_filtrado = df_eco[~mask_proyectos].copy()

        # =================================================================
        # 3. EXTRACCIÓN DE MÉTRICAS (Usando df_filtrado)
        # =================================================================
        total_recaudacion = df_filtrado[col_ingresos].sum() if col_ingresos else 0
        total_inversion = df_filtrado[col_inversion].sum() if col_inversion else 0
        total_beneficiarios = df_filtrado[col_beneficiarios].sum() if col_beneficiarios else 0

        # Filtro operativo de residuos usando columna CANTIDAD
        df_residuos = df_filtrado[df_filtrado[col_variable].str.contains("residu|limpia|recicl", case=False, na=False)] if col_variable else pd.DataFrame()
        total_toneladas = df_residuos[df_residuos[col_actividad].str.contains("tonelada", case=False, na=False)][col_cantidad].sum() if not df_residuos.empty else 0

        # Filtro operativo de servicios públicos / sanitarios
        df_sanitarios = df_filtrado[df_filtrado[col_variable].str.contains("servicios|public|sanit", case=False, na=False)] if col_variable else pd.DataFrame()
        if not df_sanitarios.empty:
            sum_beneficiarios = df_sanitarios[col_beneficiarios].sum() if col_beneficiarios in df_sanitarios.columns else 0
            sum_cantidad = df_sanitarios[col_cantidad].sum() if col_cantidad in df_sanitarios.columns else 0
            total_sanitarios = sum_beneficiarios if sum_beneficiarios > 0 else sum_cantidad
        else:
            total_sanitarios = 0

        # =================================================================
        # 4. DISEÑO DE TARJETAS DE RESUMEN INDEPENDIENTES (HORIZONTAL)
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
            html.Div("CUADRO DE MANDO OPERATIVO Y FINANCIERO", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#691c32", "marginBottom": "10px", "letterSpacing": "0.8px"}),
            
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("💰 RECAUDACIÓN TOTAL", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"${total_recaudacion:,.2f}", style={"margin": "2px 0", "fontWeight": "700", "color": "#2b6cb0", "fontSize": "18px"}),
                    html.Div("Ingresos por ventanilla", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=2, md=4, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("📉 INVERSIÓN PRESUPUESTAL", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"${total_inversion:,.2f}", style={"margin": "2px 0", "fontWeight": "700", "color": "#c53030", "fontSize": "18px"}),
                    html.Div("Egresos presupuestados", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=2, md=4, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("👥 BENEFICIARIOS SOCIALES", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_beneficiarios:,.0f} habs.", style={"margin": "2px 0", "fontWeight": "700", "color": "#691c32", "fontSize": "18px"}),
                    html.Div("Impacto directo programas", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=4, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("🗑️ RECOLECCIÓN RESIDUOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096", "textTransform": "uppercase"}),
                    html.H4(f"{total_toneladas:,.1f} Tons", style={"margin": "2px 0", "fontWeight": "700", "color": "#2f855a", "fontSize": "18px"}),
                    html.Div("Recolección y limpias", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=2, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("🚽 SERVICIOS PÚBLICOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#4a5568", "textTransform": "uppercase"}),
                    html.H4(f"{total_sanitarios:,.0f} accesos", style={"margin": "2px 0", "fontWeight": "700", "color": "#4a5568", "fontSize": "18px"}),
                    html.Div("Tráfico e infraestructura", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, lg=3, md=6, className="mb-2"),
            ], className="g-2")
        ])

        # =================================================================
        # 5. CONFIGURACIÓN DE GRÁFICAS INTEGRADAS (Incluye conteos de Proyectos)
        # =================================================================
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        df_mes = df_filtrado.groupby(col_mes)[[col_ingresos, col_inversion]].sum().reindex(orden_meses).dropna().reset_index() if col_mes else pd.DataFrame()

        fig_financiera = px.line(
            df_mes, x=col_mes, y=[col_ingresos, col_inversion], markers=True,
            color_discrete_map={col_ingresos: "#2b6cb0", col_inversion: "#c53030"},
            labels={"value": "Monto ($)", "variable": "Concepto", col_mes: ""}
        )
        fig_financiera.update_layout(
            margin=dict(l=40, r=15, t=10, b=15), plot_bgcolor="white", height=240, 
            yaxis={'gridcolor': '#f0f0f0'},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font={"size": 10})
        )

        df_acciones = df_filtrado[df_filtrado[col_cantidad] > 0]
        df_resumen_act = df_acciones.groupby(col_actividad)[col_cantidad].sum().reset_index()
        df_resumen_act = df_resumen_act.sort_values(by=col_cantidad, ascending=True).tail(5)

        fig_operativa = px.bar(
            df_resumen_act, x=col_cantidad, y=col_actividad, orientation='h',
            color_discrete_sequence=["#691c32"], labels={col_cantidad: "Metas Realizadas", col_actividad: ""}
        )
        fig_operativa.update_yaxes(
            ticktext=[f"{t[:22]}..." if len(t) > 22 else t for t in df_resumen_act[col_actividad]], 
            tickvals=df_resumen_act[col_actividad], tickfont=dict(size=10)
        )
        fig_operativa.update_layout(margin=dict(l=130, r=15, t=10, b=15), plot_bgcolor="white", height=240, xaxis={'gridcolor': '#f0f0f0'})

        # =================================================================
        # 6. CONSTRUCCIÓN DE LA TABLA EXCLUSIVA DE PROYECTOS RELEVANTES
        # =================================================================
        if not df_proyectos_raw.empty:
            df_table_proj = df_proyectos_raw[df_proyectos_raw[col_actividad] != ""].copy()
            
            tabla_cuerpo = []
            for _, row in df_table_proj.iterrows():
                mes_row = row[col_mes] if col_mes else "-"
                desc_row = row[col_actividad]
                inv_row = f"${row[col_inversion]:,.2f}" if col_inversion and row[col_inversion] > 0 else "S/I"
                
                # Si en Proyectos Relevantes la columna cantidad trae el estatus, lo mandamos directo
                cant_row = f"{row[col_cantidad]:,.0f}" if col_cantidad and isinstance(row[col_cantidad], (int, float)) and row[col_cantidad] > 0 else "En curso"
                
                tabla_cuerpo.append(html.Tr([
                    html.Td(mes_row, style={"fontSize": "11px", "fontWeight": "500"}),
                    html.Td(desc_row, style={"fontSize": "11px", "color": "#2d3748"}),
                    html.Td(cant_row, style={"fontSize": "11px", "textAlign": "center", "fontWeight": "bold", "color": "#2f855a"}),
                    html.Td(inv_row, style={"fontSize": "11px", "textAlign": "right", "color": "#4a5568"})
                ]))
            
            componente_tabla_proyectos = html.Div([
                html.Div("📋 MONITOREO DE PROYECTOS OPERATIVOS E IMPLEMENTADOS", 
                         style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                html.Div([
                    dbc.Table([
                        html.Thead(html.Tr([
                            html.Th("Mes", style={"fontSize": "10px", "textTransform": "uppercase", "backgroundColor": "#fafafa"}),
                            html.Th("Descripción del Proyecto / Acción Destacada", style={"fontSize": "10px", "textTransform": "uppercase", "backgroundColor": "#fafafa"}),
                            html.Th("Avance / Estado", style={"fontSize": "10px", "textTransform": "uppercase", "textAlign": "center", "backgroundColor": "#fafafa"}),
                            html.Th("Inversión Asignada", style={"fontSize": "10px", "textTransform": "uppercase", "textAlign": "right", "backgroundColor": "#fafafa"})
                        ])),
                        html.Tbody(tabla_cuerpo)
                    ], bordered=True, hover=True, striped=True, responsive=True, size="sm", className="mb-0")
                ], style={"padding": "10px"})
            ], className="bg-white border shadow-sm mt-3", style={"borderRadius": "6px"})
        else:
            componente_tabla_proyectos = dbc.Alert("ℹ️ No se encontraron registros vigentes en la variable de Proyectos Reelevantes.", color="light", className="mt-3")

        # =================================================================
        # 7. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            tarjetas_variables,  
            html.Hr(style={"margin": "12px 0", "opacity": "0.1"}),
            
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("📈 BALANCE FINANCIERO MENSUAL", style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                    dcc.Graph(figure=fig_financiera, config={'displayModeBar': False})
                ], className="bg-white border shadow-sm", style={"borderRadius": "6px"}), md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("🎯 PRINCIPALES METAS OPERATIVAS ALCANZADAS", style={"padding": "8px 12px", "fontWeight": "bold", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                    dcc.Graph(figure=fig_operativa, config={'displayModeBar': False})
                ], className="bg-white border shadow-sm", style={"borderRadius": "6px"}), md=6, className="mb-2")
            ]),
            
            componente_tabla_proyectos
            
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Ecología: {str(e)}", color="danger", className="m-3")
