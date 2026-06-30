import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc

def analizar_orientacion_alimentaria(df):
    """
    Módulo Operativo Premium para Orientación y Educación Alimentaria (DIF).
    - Distribución 50/50 perfectamente simétrica con cajas del mismo tamaño.
    - Corrección de Estilo Inyectado para asegurar el color azul en la tabla derecha.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Orientación Alimentaria llegó vacío.", color="warning", className="m-3")

    try:
        # 1. Copiar y normalizar nombres de columnas
        df_alim = df.copy()
        df_alim.columns = [str(c).strip().upper() for c in df_alim.columns]

        col_actividad = next((c for c in df_alim.columns if "ACTIVIDAD" in c), None)
        col_beneficiarios = next((c for c in df_alim.columns if "BENEFICIARIO" in c or "CANTIDAD" in c), None)
        col_institucion = next((c for c in df_alim.columns if "INSTITUCION" in c or "INSTITUCIÓN" in c), None)

        if col_beneficiarios:
            df_alim[col_beneficiarios] = pd.to_numeric(df_alim[col_beneficiarios], errors='coerce').fillna(0)
            col_cantidad_sistema = col_beneficiarios
        else:
            df_alim["BENEF_GENERICO"] = 0
            col_cantidad_sistema = "BENEF_GENERICO"

        if col_actividad: df_alim[col_actividad] = df_alim[col_actividad].astype(str).str.strip().str.title()
        if col_institucion: df_alim[col_institucion] = df_alim[col_institucion].astype(str).str.strip().str.title()

        # Filtrar registros activos (> 0)
        df_activos = df_alim[df_alim[col_cantidad_sistema] > 0].copy()

        # =================================================================
        # 2. MÉTRICAS SUPERIORES (KPIs)
        # =================================================================
        total_orientados = df_activos[col_cantidad_sistema].sum()
        total_temas = df_activos[col_actividad].nunique()

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
                html.Div("🍎 CIUDADANOS ORIENTADOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(f"{total_orientados:,.0f} personas", style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#73243D", "fontSize": "20px"})
            ], style=estilo_tarjeta), width=12, sm=6),
            
            dbc.Col(html.Div([
                html.Div("📚 TEMAS FORMATIVOS DESARROLLADOS", style={"fontSize": "9px", "fontWeight": "700", "color": "#718096"}),
                html.H4(f"{total_temas} Talleres Ejes", style={"margin": "2px 0 0 0", "fontWeight": "800", "color": "#2b6cb0", "fontSize": "20px"})
            ], style=estilo_tarjeta), width=12, sm=6),
        ], className="g-2 mb-3")

        # =================================================================
        # 3. COMPONENTE 1: GRÁFICA CIRCULAR (DONUT) - IZQUIERDA
        # =================================================================
        df_inst = df_activos.groupby(col_institucion)[col_cantidad_sistema].sum().reset_index()
        
        fig_donut_niveles = px.pie(
            df_inst, values=col_cantidad_sistema, names=col_institucion,
            hole=0.45,
            color_discrete_sequence=["#1a365d", "#2b6cb0", "#4a5568", "#718096"]
        )
        
        fig_donut_niveles.update_traces(
            textposition='inside',
            textinfo='percent',
            textfont=dict(size=11, weight="bold", color="white"),
            marker=dict(line=dict(color='#ffffff', width=2)),
            hovertemplate="<b>%{label}</b><br>Atendidos: %{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>"
        )
        
        fig_donut_niveles.update_layout(
            margin=dict(l=10, r=10, t=15, b=15),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.08,
                xanchor="center",
                x=0.5,
                font=dict(size=9, color="#4a5568")
            ),
            height=250
        )

        # =================================================================
        # 4. COMPONENTE 2: TABLA DERECHA CON FIJACIÓN DE COLOR AZUL (DERECHA)
        # =================================================================
        df_temas = df_activos.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_temas = df_temas.sort_values(by=col_cantidad_sistema, ascending=False)
        
        # Mantenemos la columna limpia de números para evitar conflictos con Dash
        df_temas['CANTIDAD_FORMATO'] = df_temas[col_cantidad_sistema].apply(lambda x: f"{x:,.0f}")

        tabla_ejecutiva = dash_table.DataTable(
            data=df_temas.to_dict('records'),
            columns=[
                {"name": "Temática del Taller Impartido", "id": col_actividad},
                {"name": "Beneficiarios", "id": "CANTIDAD_FORMATO"}
            ],
            style_as_list_view=True,
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': '750',
                'color': '#4a5568',
                'fontSize': '11px',
                'borderBottom': '2px solid #dee2e6',
                'padding': '10px'
            },
            style_cell={
                'padding': '10px 12px',
                'fontSize': '11px',
                'color': '#2d3748',
                'fontFamily': 'Helvetica, Arial, sans-serif'
            },
            # style_cell_conditional genérico para alineación básica
            style_cell_conditional=[
                {'if': {'column_id': col_actividad}, 'textAlign': 'left'},
                {'if': {'column_id': 'CANTIDAD_FORMATO'}, 'textAlign': 'right'}
            ],
            # SOLUClÓN: Usamos style_data_conditional para forzar el color de la fuente al renderizar datos
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'CANTIDAD_FORMATO'
                    },
                    'color': '#2b6cb0',
                    'fontWeight': 'bold'
                }
            ],
            style_table={
                'maxHeight': '250px',
                'overflowY': 'auto'
            }
        )

        # =================================================================
        # 5. MAQUETACIÓN SIMÉTRICA HOMOLOGADA (Mismo tamaño garantizado)
        # =================================================================
        estilo_contenedor_fijo = {
            "borderRadius": "6px", 
            "height": "100%", 
            "display": "flex", 
            "flexDirection": "column",
            "justifyContent": "space-between"
        }

        bloque_dashboard = dbc.Row([
            # Izquierda: Recuadro de Gráfica (50% de ancho)
            dbc.Col(html.Div([
                html.Div("🏫 PARTICIPACIÓN POR NIVEL / ENTORNO EDUCATIVO", 
                         style={"padding": "10px 14px", "fontWeight": "700", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                html.Div(dcc.Graph(figure=fig_donut_niveles, config={'displayModeBar': False}), style={"padding": "5px", "flexGrow": "1"})
            ], className="bg-white border shadow-sm", style=estilo_contenedor_fijo), width=12, lg=6),

            # Derecha: Recuadro de Tabla Forzada a Color Azul (50% de ancho)
            dbc.Col(html.Div([
                html.Div("📊 ALCANCE OPERATIVO DETALLADO POR TALLER", 
                         style={"padding": "10px 14px", "fontWeight": "700", "backgroundColor": "#f8f9fa", "borderBottom": "1px solid #dee2e6", "fontSize": "11px", "color": "#4a5568"}),
                html.Div(tabla_ejecutiva, style={"padding": "8px", "flexGrow": "1"})
            ], className="bg-white border shadow-sm", style=estilo_contenedor_fijo), width=12, lg=6),
        ], className="g-3")

        return html.Div([
            html.Div("ESTADÍSTICAS DE CAPACITACIÓN - ORIENTACIÓN Y EDUCACIÓN ALIMENTARIA", 
                     style={"fontSize": "11px", "fontWeight": "700", "color": "#73243D", "marginBottom": "14px", "letterSpacing": "0.8px"}),
            seccion_kpis,
            bloque_dashboard
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al procesar el módulo simétrico: {str(e)}", color="danger", className="m-3")
