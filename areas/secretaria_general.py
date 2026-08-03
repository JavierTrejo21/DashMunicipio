# areas/secretaria_general.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

# Colorimetría institucional Matriz
VERDE_MATRIZ = "#115e59"      # Verde petróleo principal 
GUINDA_MATRIZ = "#691c32"     # Guinda institucional
TEXTO_DARK = "#1f2937"
TEXTO_SECUNDARIO = "#374151"  # <-- Color más oscuro y legible para la columna del centro
GRIS_CLARO = "#f9fafb"

def analizar_secretaria_general(df):
    """
    Módulo operativo para la Secretaría General.
    - Cuadrícula compacta de KPIs en 2x2.
    - Tabla nativa HTML purificada con contraste mejorado.
    - Identidad oficial institucional (Verde Petróleo y Guinda).
    - Gráfica de barras agrupadas con orden cronológico estricto para análisis preciso.
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
            "borderRadius": "8px",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.04)",
            "border": "1px solid #eef2f5",
            "backgroundColor": "#ffffff",
            "padding": "12px 16px",
            "height": "100%"
        }

        cuadrícula_kpis = html.Div([
            html.Div("CUADRO DE MANDO - SECRETARÍA GENERAL MUNICIPAL", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": GUINDA_MATRIZ, "marginBottom": "12px", "letterSpacing": "0.8px"}),
            
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("🗣️ AUDIENCIAS CON LA CIUDADANÍA", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{int(total_audiencias):,} atendidas", style={"margin": "2px 0", "fontWeight": "bold", "color": VERDE_MATRIZ, "fontSize": "18px"}),
                    html.Div("Atención directa del Secretario", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("📄 CONSTANCIAS Y TRÁMITES", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{int(total_documentos):,} emitidas", style={"margin": "2px 0", "fontWeight": "bold", "color": GUINDA_MATRIZ, "fontSize": "18px"}),
                    html.Div("Certeza jurídica e identidad", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),
            ], className="g-2"),

            dbc.Row([
                dbc.Col(html.Div([
                    html.Div("🏛️ SESIONES DE CABILDO EFECTUADAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{int(total_cabildo):,} sesiones", style={"margin": "2px 0", "fontWeight": "bold", "color": VERDE_MATRIZ, "fontSize": "18px"}),
                    html.Div("Ordinarias y Extraordinarias", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),

                dbc.Col(html.Div([
                    html.Div("⚡ TOTAL GESTIONES ADMINISTRATIVAS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                    html.H4(f"{int(total_gestiones):,} acciones", style={"margin": "2px 0", "fontWeight": "bold", "color": TEXTO_DARK, "fontSize": "18px"}),
                    html.Div("Impacto operativo total en el área", style={"fontSize": "9px", "color": "#a0aec0"})
                ], style=estilo_tarjeta), width=12, md=6, className="mb-2"),
            ], className="g-2")
        ])

        # =================================================================
        # 5. CONSTRUCCIÓN DE LA TABLA (Con contraste optimizado)
        # =================================================================
        df_resumen = df_sg.groupby([col_actividad, col_variable])[col_cantidad_sistema].sum().reset_index()
        df_resumen = df_resumen.sort_values(by=col_cantidad_sistema, ascending=False)

        filas_tabla = []
        for _, r in df_resumen.iterrows():
            filas_tabla.append(html.Tr([
                html.Td(r[col_actividad], style={"fontSize": "11px", "color": TEXTO_DARK, "textAlign": "left", "padding": "8px 14px", "fontWeight": "500", "backgroundColor": "#ffffff", "border": "1px solid #e5e7eb"}),
                # CAMBIO APLICADO AQUÍ: Usamos TEXTO_SECUNDARIO (#374151) con font-weight 500 para mayor legibilidad
                html.Td(r[col_variable], style={"fontSize": "11px", "color": TEXTO_SECUNDARIO, "fontWeight": "500", "padding": "8px 14px", "backgroundColor": "#ffffff", "textAlign": "left", "border": "1px solid #e5e7eb"}),
                html.Td(f"{r[col_cantidad_sistema]:,.0f}", style={"fontSize": "11px", "color": VERDE_MATRIZ, "fontWeight": "bold", "padding": "8px 14px", "backgroundColor": "#ffffff", "textAlign": "center", "border": "1px solid #e5e7eb"}),
            ]))

        filas_tabla.append(html.Tr([
            html.Td("TOTAL DE ATENCIONES Y GESTIONES GENERALES", style={"fontSize": "11px", "fontWeight": "bold", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": GUINDA_MATRIZ, "border": f"1px solid {GUINDA_MATRIZ}"}),
            html.Td("Consolidado Anual del Área", style={"fontSize": "11px", "fontWeight": "bold", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": GUINDA_MATRIZ, "border": f"1px solid {GUINDA_MATRIZ}"}),
            html.Td(f"{int(total_gestiones):,}", style={"fontSize": "11px", "fontWeight": "bold", "color": "#ffffff", "backgroundColor": GUINDA_MATRIZ, "textAlign": "center", "border": f"1px solid {GUINDA_MATRIZ}"}),
        ]))

        tabla_layout = html.Div([
            html.Div("BALANCE ANUAL DE INDICADORES EN SECRETARÍA GENERAL", 
                     style={"padding": "12px 14px", "fontWeight": "bold", "backgroundColor": VERDE_MATRIZ, "color": "white", "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px", "fontSize": "0.85rem"}),
            html.Div(
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Actividad Registrada", style={"fontSize": "10px", "color": TEXTO_DARK, "textAlign": "left", "padding": "10px 14px", "fontWeight": "bold", "backgroundColor": GRIS_CLARO, "border": "1px solid #e5e7eb", "width": "50%"}),
                        html.Th("Eje Operativo / Clasificación", style={"fontSize": "10px", "color": TEXTO_DARK, "textAlign": "left", "padding": "10px 14px", "fontWeight": "bold", "backgroundColor": GRIS_CLARO, "border": "1px solid #e5e7eb", "width": "35%"}),
                        html.Th("Total Absoluto", style={"fontSize": "10px", "color": TEXTO_DARK, "padding": "10px 14px", "fontWeight": "bold", "backgroundColor": GRIS_CLARO, "border": "1px solid #e5e7eb", "textAlign": "center", "width": "15%"}),
                    ])),
                    html.Tbody(filas_tabla)
                ], 
                style={"width": "100%", "margin": "0", "borderCollapse": "collapse", "backgroundColor": "#ffffff"}
                ),
                style={"padding": "0px"}
            )
        ], style={"border": "1px solid #e5e7eb", "borderRadius": "8px", "marginTop": "16px", "backgroundColor": "#ffffff", "overflow": "hidden"})

        # =================================================================
        # 6. GRÁFICA INFERIOR: BARRAS AGRUPADAS CON CRONOLOGÍA ESTRICTA
        # =================================================================
        if col_mes and col_variable:
            df_barras = df_sg.groupby([col_mes, col_variable])[col_cantidad_sistema].sum().reset_index()
            df_barras[col_mes] = pd.Categorical(df_barras[col_mes], categories=orden_meses, ordered=True)
            df_barras = df_barras.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_barras = pd.DataFrame()

        if not df_barras.empty and df_barras[col_cantidad_sistema].sum() > 0:
            fig_comparativa = px.bar(
                df_barras, x=col_mes, y=col_cantidad_sistema, color=col_variable,
                barmode='group',
                color_discrete_map={
                    "Atención Personal A La Población": VERDE_MATRIZ,
                    "Actividades Administrativas": "#14b8a6",
                    "Sesiones De Cabildo": GUINDA_MATRIZ
                },
                labels={col_cantidad_sistema: "Volumen", col_mes: "", col_variable: "Clasificación"}
            )
            fig_comparativa.update_layout(
                margin=dict(l=40, r=15, t=15, b=30),
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=280,
                yaxis={'gridcolor': '#f0f0f0'},
                xaxis=dict(tickangle=0, categoryorder='array', categoryarray=orden_meses),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
            )
            seccion_grafica = html.Div([
                html.Div("DINÁMICA DE TRABAJO MENSUAL (COMPARATIVA POR EJE OPERATIVO)", 
                         style={"padding": "12px 14px", "fontWeight": "bold", "backgroundColor": GUINDA_MATRIZ, "color": "white", "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px", "fontSize": "0.85rem"}),
                html.Div(dcc.Graph(figure=fig_comparativa, config={'displayModeBar': False}), style={"padding": "10px"})
            ], className="border shadow-sm mt-3", style={"borderRadius": "8px", "backgroundColor": "#ffffff"})
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