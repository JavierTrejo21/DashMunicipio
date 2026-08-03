# areas/dif_psicologia.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

# Colorimetría institucional Matriz
VERDE_MATRIZ = "#115e59"      # Verde petróleo principal (Cabeceras / Gráficos / Destacados)
GUINDA_MATRIZ = "#691c32"     # Guinda institucional (Sub-encabezados / Totales / Acentos)
TEXTO_DARK = "#1f2937"
GRIS_CLARO = "#f9fafb"

def analizar_dif_psicologia(df):
    """
    Módulo híbrido de Alto Impacto para DIF Psicología.
    - Alineado con la paleta Verde Petróleo y Guinda institucional.
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
        # 2. CÓMPUTO DE REGLAS DE NEGOCIO (KPIs) CON BARRAS INSTITUCIONALES
        # =================================================================
        total_consultas = df_temas[col_cantidad_sistema].sum()
        total_pacientes = df_demo[col_cantidad_sistema].sum()
        
        df_top_trastorno = df_temas.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        if not df_top_trastorno.empty:
            top_row = df_top_trastorno.sort_values(by=col_cantidad_sistema, ascending=False).iloc[0]
            top_incidencia = f"{top_row[col_actividad]}"
        else:
            top_incidencia = "N/A"

        seccion_kpis = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("TOTAL CONSULTAS CLÍNICAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                    html.H4(f"{int(total_consultas):,} sesiones", style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem", "margin": "0"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, sm=4),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("CIUDADANOS ATENDIDOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                    html.H4(f"{int(total_pacientes):,} personas", style={"color": GUINDA_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem", "margin": "0"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {GUINDA_MATRIZ}"}), width=12, sm=4),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("PRINCIPAL DIAGNÓSTICO", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                    html.H4(top_incidencia, style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "0.95rem", "margin": "0", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, sm=4),
        ], className="g-2 mb-3")

        # =================================================================
        # 3. PANEL IZQUIERDO: TABLA DE RESUMEN DEMOGRÁFICO INSTITUCIONAL
        # =================================================================
        df_demo_agrupado = df_demo.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_demo_agrupado = df_demo_agrupado.sort_values(by=col_cantidad_sistema, ascending=False)

        filas_tabla_demo = []
        for _, r in df_demo_agrupado.iterrows():
            filas_tabla_demo.append(html.Tr([
                html.Td(r[col_actividad], style={"fontSize": "11px", "color": TEXTO_DARK, "textAlign": "left", "padding": "10px 14px", "fontWeight": "500", "backgroundColor": "#ffffff", "border": "1px solid #e5e7eb"}),
                html.Td(f"{r[col_cantidad_sistema]:,.0f}", style={"fontSize": "11px", "color": VERDE_MATRIZ, "fontWeight": "700", "padding": "10px 14px", "backgroundColor": "#ffffff", "textAlign": "center", "border": "1px solid #e5e7eb"}),
            ]))

        # Fila de Cierre para el total demográfico en Guinda Institucional
        filas_tabla_demo.append(html.Tr([
            html.Td("TOTAL PACIENTES ÚNICOS", style={"fontSize": "11px", "fontWeight": "bold", "color": "#ffffff", "textAlign": "left", "padding": "10px 14px", "backgroundColor": GUINDA_MATRIZ, "border": f"1px solid {GUINDA_MATRIZ}"}),
            html.Td(f"{int(total_pacientes):,}", style={"fontSize": "11px", "fontWeight": "bold", "color": "#ffffff", "backgroundColor": GUINDA_MATRIZ, "textAlign": "center", "border": f"1px solid {GUINDA_MATRIZ}"}),
        ]))

        tabla_layout_sencilla = html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Grupo Vulnerable / Edad y Género", style={"fontSize": "10px", "color": TEXTO_DARK, "textAlign": "left", "padding": "10px 14px", "fontWeight": "bold", "backgroundColor": GRIS_CLARO, "border": "1px solid #e5e7eb", "width": "75%"}),
                    html.Th("Total", style={"fontSize": "10px", "color": TEXTO_DARK, "padding": "10px 14px", "fontWeight": "bold", "backgroundColor": GRIS_CLARO, "border": "1px solid #e5e7eb", "textAlign": "center", "width": "25%"}),
                ])),
                html.Tbody(filas_tabla_demo)
            ], 
            style={"width": "100%", "margin": "0", "borderCollapse": "collapse", "backgroundColor": "#ffffff"}
            )
        ], style={"border": "1px solid #e5e7eb", "borderRadius": "6px", "overflow": "hidden"})

        # =================================================================
        # 4. PANEL DERECHO: EMBUDO (FUNNEL) CON TONALIDAD VERDE PETRÓLEO
        # =================================================================
        df_temas_agrupado = df_temas.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_temas_agrupado = df_temas_agrupado.sort_values(by=col_cantidad_sistema, ascending=False)

        fig_embudo = px.funnel(
            df_temas_agrupado, x=col_cantidad_sistema, y=col_actividad,
            color_discrete_sequence=[VERDE_MATRIZ],
            labels={col_cantidad_sistema: "Casos", col_actividad: "Diagnóstico"}
        )
        fig_embudo.update_layout(
            margin=dict(l=10, r=20, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=300,
            font=dict(size=11, color=TEXTO_DARK)
        )
        fig_embudo.update_yaxes(automargin=True)

        # =================================================================
        # 5. INTEGRACIÓN DEL LAYOUT BILATERAL HOMOLOGADO
        # =================================================================
        estilo_contenedor_fijo = {
            "borderRadius": "8px", 
            "height": "100%", 
            "display": "flex", 
            "flexDirection": "column",
            "backgroundColor": "#ffffff"
        }

        bloque_dashboard = dbc.Row([
            # Columna de la Tabla Resumen (Izquierda) con Encabezado Verde Petróleo
            dbc.Col(html.Div([
                html.Div("RESUMEN DE MATRÍCULA Y PERFIL DE PACIENTES", 
                         style={"padding": "12px 14px", "fontWeight": "bold", "backgroundColor": VERDE_MATRIZ, "color": "white", "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px", "fontSize": "0.85rem"}),
                html.Div(tabla_layout_sencilla, style={"padding": "12px", "flexGrow": "1"})
            ], className="border shadow-sm", style=estilo_contenedor_fijo), width=12, lg=5, className="mb-3"),

            # Columna del Embudo (Derecha) con Encabezado Guinda
            dbc.Col(html.Div([
                html.Div("EMBUDO DE PROBLEMÁTICAS Y SALUD MENTAL DETECTADA", 
                         style={"padding": "12px 14px", "fontWeight": "bold", "backgroundColor": GUINDA_MATRIZ, "color": "white", "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px", "fontSize": "0.85rem"}),
                html.Div(dcc.Graph(figure=fig_embudo, config={'displayModeBar': False}), style={"padding": "10px", "flexGrow": "1"})
            ], className="border shadow-sm", style=estilo_contenedor_fijo), width=12, lg=7, className="mb-3"),
        ], className="g-3")

        return html.Div([
            seccion_kpis,
            bloque_dashboard
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error en la consolidación del módulo de DIF Psicología: {str(e)}", color="danger", className="m-3")