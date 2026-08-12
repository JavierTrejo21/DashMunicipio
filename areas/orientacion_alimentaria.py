import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc

# Colorimetría institucional Matriz
VERDE_MATRIZ = "#115e59"      # Verde petróleo principal 
GUINDA_MATRIZ = "#691c32"     # Guinda institucional
GRIS_OSCURO = "#4a5568"
TEXTO_DARK = "#1f2937"
GRIS_CLARO = "#f9fafb"

def analizar_orientacion_alimentaria(df):
    """
    Módulo Operativo para Orientación y Educación Alimentaria (DIF).
    - Incluye gráfica de anillo infográfico con total centralizado.
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

        df_activos = df_alim[df_alim[col_cantidad_sistema] > 0].copy()

        # =================================================================
        # 2. MÉTRICAS SUPERIORES (KPIs)
        # =================================================================
        total_orientados = df_activos[col_cantidad_sistema].sum()
        total_temas = df_activos[col_actividad].nunique()

        seccion_kpis = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("CIUDADANOS ORIENTADOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                    html.H4(f"{int(total_orientados):,} personas", style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem", "margin": "0"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, sm=6),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("TEMAS FORMATIVOS DESARROLLADOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                    html.H4(f"{total_temas} Talleres Ejes", style={"color": GUINDA_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem", "margin": "0"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {GUINDA_MATRIZ}"}), width=12, sm=6),
        ], className="g-2 mb-3")

        # =================================================================
        # 3. COMPONENTE 1: ANILLO INFOGRÁFICO CON TOTAL CENTRALIZADO - IZQUIERDA
        # =================================================================
        df_inst = df_activos.groupby(col_institucion)[col_cantidad_sistema].sum().reset_index()
        
        # Paleta combinada institucional (Verde, Guinda, Tonos intermedios)
        colores_anillo = ["#115e59", "#691c32", "#bc955c", "#2b6cb0", "#4a5568"]

        fig_donut = px.pie(
            df_inst, values=col_cantidad_sistema, names=col_institucion,
            hole=0.6,
            color_discrete_sequence=colores_anillo
        )
        
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent',
            textfont=dict(size=11, family="sans-serif", color="white"),
            marker=dict(line=dict(color='#ffffff', width=2)),
            hovertemplate="<b>%{label}</b><br>Atendidos: %{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>"
        )
        
        # Añadir el texto del Total al centro del anillo
        fig_donut.add_annotation(
            text=f"<b>{int(total_orientados):,}</b><br><span style='font-size:10px; color:#4a5568;'>Total</span>",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color=TEXTO_DARK, family="sans-serif")
        )

        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                font=dict(size=10, color=GRIS_OSCURO)
            ),
            height=260,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # =================================================================
        # 4. COMPONENTE 2: TABLA DERECHA
        # =================================================================
        df_temas = df_activos.groupby(col_actividad)[col_cantidad_sistema].sum().reset_index()
        df_temas = df_temas.sort_values(by=col_cantidad_sistema, ascending=False)
        
        df_temas['CANTIDAD_FORMATO'] = df_temas[col_cantidad_sistema].apply(lambda x: f"{x:,.0f}")

        tabla_ejecutiva = dash_table.DataTable(
            data=df_temas.to_dict('records'),
            columns=[
                {"name": "Temática del Taller Impartido", "id": col_actividad},
                {"name": "Beneficiarios", "id": "CANTIDAD_FORMATO"}
            ],
            style_as_list_view=True,
            style_header={
                'backgroundColor': GRIS_CLARO,
                'fontWeight': 'bold',
                'color': TEXTO_DARK,
                'fontSize': '11px',
                'borderBottom': f'2px solid {VERDE_MATRIZ}',
                'padding': '10px'
            },
            style_cell={
                'padding': '10px 12px',
                'fontSize': '11px',
                'color': TEXTO_DARK,
                'fontFamily': 'Helvetica, Arial, sans-serif'
            },
            style_cell_conditional=[
                {'if': {'column_id': col_actividad}, 'textAlign': 'left'},
                {'if': {'column_id': 'CANTIDAD_FORMATO'}, 'textAlign': 'right'}
            ],
            style_data_conditional=[
                {
                    'if': {'column_id': 'CANTIDAD_FORMATO'},
                    'color': VERDE_MATRIZ,
                    'fontWeight': 'bold'
                }
            ],
            style_table={
                'maxHeight': '260px',
                'overflowY': 'auto'
            }
        )

        # =================================================================
        # 5. MAQUETACIÓN SIMÉTRICA HOMOLOGADA
        # =================================================================
        estilo_contenedor_fijo = {
            "borderRadius": "8px", 
            "height": "100%", 
            "display": "flex", 
            "flexDirection": "column",
            "backgroundColor": "#ffffff"
        }

        bloque_dashboard = dbc.Row([
            # Izquierda: Anillo Infográfico con Encabezado Guinda
            dbc.Col(html.Div([
                html.Div("DISTRIBUCIÓN POR NIVEL / ENTORNO EDUCATIVO (ANILLO INFOGRÁFICO)", 
                         style={"padding": "12px 14px", "fontWeight": "bold", "backgroundColor": GUINDA_MATRIZ, "color": "white", "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px", "fontSize": "0.85rem"}),
                html.Div(dcc.Graph(figure=fig_donut, config={'displayModeBar': False}), style={"padding": "10px", "flexGrow": "1"})
            ], className="border shadow-sm", style=estilo_contenedor_fijo), width=12, lg=6, className="mb-3"),

            # Derecha: Tabla con Encabezado Verde Petróleo
            dbc.Col(html.Div([
                html.Div("ALCANCE OPERATIVO DETALLADO POR TALLER", 
                         style={"padding": "12px 14px", "fontWeight": "bold", "backgroundColor": VERDE_MATRIZ, "color": "white", "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px", "fontSize": "0.85rem"}),
                html.Div(tabla_ejecutiva, style={"padding": "10px", "flexGrow": "1"})
            ], className="border shadow-sm", style=estilo_contenedor_fijo), width=12, lg=6, className="mb-3"),
        ], className="g-3")

        return html.Div([
            seccion_kpis,
            bloque_dashboard
        ], style={"padding": "5px"})

    except Exception as e:
        return dbc.Alert(f"❌ Error al procesar el módulo infográfico: {str(e)}", color="danger", className="m-3")