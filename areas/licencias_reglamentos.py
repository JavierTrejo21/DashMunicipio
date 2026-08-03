# areas/licencias_reglamentos.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc

# Paleta institucional unificada Matriz
VERDE_INST = "#115e59"      # Verde petróleo principal 
VERDE_CLARO = "#14b8a6"
GUINDA_INST = "#691c32"     # Guinda institucional
DORADO_INST = "#bc955c"     # Dorado institucional
TEXTO_DARK = "#1f2937"
TEXTO_SECUNDARIO = "#374151"  # <-- Color oscuro optimizado para alta visibilidad
GRIS_BORDES = "#e5e7eb"

def analizar_licencias_reglamentos(df):
    """
    Módulo operativo para Licencias y Reglamentos.
    Analiza trámites comerciales, uso de infraestructura y recaudación económica
    bajo la identidad institucional unificada y con contraste de texto optimizado.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Licencias y Reglamentos llegó vacío al módulo operativo.", color="warning", className="m-3")

    try:
        # 1. Copiar y limpiar nombres de columnas
        df_lr = df.copy()
        df_lr.columns = [str(c).strip().upper().replace('\n', '').replace('\r', '') for c in df_lr.columns]

        # Identificación dinámica de columnas
        col_mes = next((c for c in df_lr.columns if "MES" in c), None)
        col_atendidos = next((c for c in df_lr.columns if "ATENDID" in c or "CANTIDAD" in c), None)
        col_actividad = next((c for c in df_lr.columns if "ACTIVIDAD" in c), None)
        col_variable = next((c for c in df_lr.columns if "VARIABLE" in c), None)
        col_inversion = next((c for c in df_lr.columns if "INVERSION" in c or "MONTO" in c or "INGRESO" in c), None)

        # 2. Conversión limpia de datos y limpieza de moneda ($)
        if col_atendidos:
            df_lr[col_atendidos] = pd.to_numeric(df_lr[col_atendidos], errors='coerce').fillna(0)
            df_lr["CANTIDAD"] = df_lr[col_atendidos]
            col_cantidad_sistema = "CANTIDAD"
        else:
            df_lr["CANTIDAD"] = 0
            col_cantidad_sistema = "CANTIDAD"

        # Limpiador robusto de la columna INVERSION (Moneda)
        if col_inversion:
            df_lr[col_inversion] = df_lr[col_inversion].astype(str)\
                .str.replace('$', '', regex=False)\
                .str.replace(',', '', regex=False)\
                .str.replace('-', '0', regex=False)\
                .str.strip()
            df_lr[col_inversion] = pd.to_numeric(df_lr[col_inversion], errors='coerce').fillna(0.0)
        else:
            df_lr["INVERSION_LIMPIA"] = 0.0
            col_inversion = "INVERSION_LIMPIA"

        if col_variable: df_lr[col_variable] = df_lr[col_variable].astype(str).str.strip()
        if col_actividad: df_lr[col_actividad] = df_lr[col_actividad].astype(str).str.strip()
        if col_mes: df_lr[col_mes] = df_lr[col_mes].astype(str).str.strip().str.title()

        # =================================================================
        # 3. EXTRACCIÓN DE MÉTRICAS OPERATIVAS Y FINANCIERAS
        # =================================================================
        total_tramites = df_lr[col_cantidad_sistema].sum()
        total_recaudado = df_lr[col_inversion].sum()

        # Conteo de Infraestructura Municipal (Canchas, Espacios públicos)
        df_infra = df_lr[df_lr[col_variable].str.contains("infraes|cancha|permiso", case=False, na=False)] if col_variable else pd.DataFrame()
        total_infra = df_infra[col_cantidad_sistema].sum() if not df_infra.empty else 0

        # Conteo de Cobros de Piso ejecutados
        df_piso = df_lr[df_lr[col_variable].str.contains("piso|cobro", case=False, na=False)] if col_variable else pd.DataFrame()
        total_piso = df_piso[col_cantidad_sistema].sum() if not df_piso.empty else 0

        # =================================================================
        # 4. DISEÑO DE TARJETAS SUPERIORES (Con texto de alto contraste)
        # =================================================================
        kpis_row = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("GESTIONES TOTALES", className="mb-1", style={"fontSize": "0.7rem", "fontWeight": "700", "color": TEXTO_SECUNDARIO}),
                    html.H4(f"{total_tramites:,.0f} actos", style={"color": VERDE_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
                ])
            ], className="border-0 shadow-sm mb-3 position-relative", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_INST}"}), width=12, md=3),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("RECAUDACIÓN TOTAL", className="mb-1", style={"fontSize": "0.7rem", "fontWeight": "700", "color": TEXTO_SECUNDARIO}),
                    html.H4(f"${total_recaudado:,.2f}", style={"color": VERDE_CLARO, "fontWeight": "bold", "fontSize": "1.1rem"})
                ])
            ], className="border-0 shadow-sm mb-3 position-relative", style={"borderRadius": "12px", "borderLeft": f"4px solid {VERDE_CLARO}"}), width=12, md=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("COBROS DE PISO", className="mb-1", style={"fontSize": "0.7rem", "fontWeight": "700", "color": TEXTO_SECUNDARIO}),
                    html.H4(f"{total_piso:,.0f} cobros", style={"color": DORADO_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
                ])
            ], className="border-0 shadow-sm mb-3 position-relative", style={"borderRadius": "12px", "borderLeft": f"4px solid {DORADO_INST}"}), width=12, md=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("INFRAESTRUCTURA", className="mb-1", style={"fontSize": "0.7rem", "fontWeight": "700", "color": TEXTO_SECUNDARIO}),
                    html.H4(f"{total_infra:,.0f} permisos", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.1rem"})
                ])
            ], className="border-0 shadow-sm mb-3 position-relative", style={"borderRadius": "12px", "borderLeft": f"4px solid {TEXTO_DARK}"}), width=12, md=3),
        ], className="mb-2")

        # =================================================================
        # 5. CONFIGURACIÓN DE GRÁFICAS (Con etiquetas oscuras y legibles)
        # =================================================================
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Gráfica Temporal de Recaudación ($) por Mes
        if col_mes:
            df_mes = df_lr.groupby(col_mes)[col_inversion].sum().reset_index()
            df_mes[col_mes] = pd.Categorical(df_mes[col_mes], categories=orden_meses, ordered=True)
            df_mes = df_mes.sort_values(col_mes).dropna().reset_index(drop=True)
        else:
            df_mes = pd.DataFrame()

        if not df_mes.empty and df_mes[col_inversion].sum() > 0:
            fig_mensual = px.line(
                df_mes, x=col_mes, y=col_inversion, markers=True,
                color_discrete_sequence=[VERDE_INST],
                labels={col_inversion: "Ingresos ($)", col_mes: ""}
            )
            fig_mensual.update_layout(
                title=dict(text="<b>COMPORTAMIENTO MENSUAL DE INGRESOS (TESORERÍA)</b>", font=dict(size=11, color=TEXTO_DARK)),
                margin=dict(l=50, r=15, t=35, b=15), plot_bgcolor="white", paper_bgcolor="white", height=260, 
                yaxis={'gridcolor': '#f0f0f0', 'tickprefix': '$', 'tickfont': dict(color=TEXTO_SECUNDARIO)},
                xaxis={'tickfont': dict(color=TEXTO_SECUNDARIO)}
            )
            graph_left = dcc.Graph(figure=fig_mensual, config={'displayModeBar': False})
        else:
            graph_left = html.Div("ℹ️ No hay transacciones económicas registradas para graficar la tendencia mensual.", style={"padding": "40px 20px", "textAlign": "center", "color": "#a0aec0", "fontSize": "12px"})

        # Gráfica Top Actividades con Mayor Recaudación ($)
        if col_actividad:
            df_act5 = df_lr.groupby(col_actividad)[col_inversion].sum().reset_index()
            df_act5 = df_act5[df_act5[col_inversion] > 0].sort_values(by=col_inversion, ascending=True).tail(5)
            df_act5[col_actividad] = df_act5[col_actividad].str.title()
        else:
            df_act5 = pd.DataFrame()

        if not df_act5.empty:
            fig_actividades = px.bar(
                df_act5, x=col_inversion, y=col_actividad, orientation='h',
                color_discrete_sequence=[GUINDA_INST],
                labels={col_inversion: "Total Recaudado ($)", col_actividad: ""}
            )
            # Etiquetas del eje Y en tono oscuro intenso para máxima visibilidad
            fig_actividades.update_yaxes(tickvals=df_act5[col_actividad], tickfont=dict(size=10, color=TEXTO_DARK, family="sans-serif"))
            fig_actividades.update_layout(
                title=dict(text="<b>PRINCIPALES GIROS COMERCIALES POR RECAUDACIÓN</b>", font=dict(size=11, color=TEXTO_DARK)),
                margin=dict(l=170, r=15, t=35, b=15), plot_bgcolor="white", paper_bgcolor="white", height=260, 
                xaxis={'gridcolor': '#f0f0f0', 'tickprefix': '$', 'tickfont': dict(color=TEXTO_SECUNDARIO)}
            )
            graph_right = dcc.Graph(figure=fig_actividades, config={'displayModeBar': False})
        else:
            graph_right = html.Div("ℹ️ No hay ingresos monetarios suficientes para desglosar el Top de Actividades.", style={"padding": "40px 20px", "textAlign": "center", "color": "#a0aec0", "fontSize": "12px"})

        # =================================================================
        # 6. LAYOUT CONSOLIDADO FINAL
        # =================================================================
        return html.Div([
            kpis_row,  
            html.Hr(style={"margin": "15px 0", "opacity": "0.1"}),
            
            dbc.Row([
                # Panel Izquierdo: Flujo Financiero Mensual
                dbc.Col(html.Div([
                    graph_left
                ], className="bg-white border shadow-sm p-2", style={"borderRadius": "14px"}), md=6, className="mb-2"),

                # Panel Derecho: Rendimiento por Actividad
                dbc.Col(html.Div([
                    graph_right
                ], className="bg-white border shadow-sm p-2", style={"borderRadius": "14px"}), md=6, className="mb-2")
            ])
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el cuadro de mando de Licencias y Reglamentos: {str(e)}", color="danger", className="m-3")