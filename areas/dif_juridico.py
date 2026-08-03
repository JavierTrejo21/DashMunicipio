import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

# Colorimetría institucional Matriz
VERDE_MATRIZ = "#115e59"      # Verde petróleo principal (Cabeceras de tabla / KPIs)
GUINDA_MATRIZ = "#691c32"     # Guinda institucional (Sub-encabezados / Acentos)
TEXTO_DARK = "#1f2937"
GRIS_CLARO = "#f9fafb"

def analizar_dif_juridico(df):
    """Módulo estructurado para DIF Jurídico con tarjetas de resumen y desglose de servicios."""
    
    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()

    columnas_reales = df.columns.tolist()
    
    col_actividad = next((c for c in columnas_reales if "ACTIVIDAD" in str(c).upper()), "Actividad")
    col_cantidad = next((c for c in columnas_reales if "CANTIDAD" in str(c).upper()), "Cantidad")
    col_mes = next((c for c in columnas_reales if "MES" in str(c).upper()), "Mes")

    df_limpio = pd.DataFrame()
    df_limpio['Actividad'] = df[col_actividad].astype(str).str.strip() if col_actividad in df.columns else "General"
    df_limpio['Cantidad'] = pd.to_numeric(df[col_cantidad], errors='coerce').fillna(0) if col_cantidad in df.columns else 0
    df_limpio['Mes'] = df[col_mes].astype(str).str.strip().str.title() if col_mes in df.columns else "General"

    # Métricas clave globales
    total_asesorias = df_limpio[df_limpio['Actividad'].str.contains("asesorias juridicas", case=False, na=False)]['Cantidad'].sum()
    total_canalizaciones = df_limpio[df_limpio['Actividad'].str.contains("Canalización", case=False, na=False)]['Cantidad'].sum()
    total_pensiones = df_limpio[df_limpio['Actividad'].str.contains("pensión alimenticia", case=False, na=False)]['Cantidad'].sum()
    total_registros_gral = df_limpio['Cantidad'].sum()

    # --- KPI CARDS SUPERIORES ---
    kpis_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("TOTAL DE ASESORÍAS JURÍDICAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_asesorias):,} asesorías", style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("CASOS CANALIZADOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_canalizaciones):,} casos", style={"color": GUINDA_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {GUINDA_MATRIZ}"}), width=12, md=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("TRÁMITES DE PENSIÓN ALIMENTICIA", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_pensiones):,} trámites", style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, md=4),
    ], className="mb-3")

    # Consolidado acumulado por tipo de actividad jurídica
    df_resumen = df_limpio.groupby('Actividad')['Cantidad'].sum().reset_index()
    df_resumen = df_resumen.sort_values(by='Cantidad', ascending=False)

    filas_tabla = []
    for _, row in df_resumen.iterrows():
        filas_tabla.append(html.Tr([
            html.Td(row['Actividad'], style={"fontSize": "0.8rem", "fontWeight": "500"}),
            html.Td(f"{int(row['Cantidad']):,}", style={"fontSize": "0.8rem", "fontWeight": "bold", "color": VERDE_MATRIZ, "textAlign": "right"})
        ]))

    # Tabla con diseño institucional
    tabla_consolidada = html.Div([
        html.Div([
            html.Span("CONSOLIDADO ACUMULADO DE ACTIVIDADES - ÁREA JURÍDICA", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "white"})
        ], className="p-3", style={"backgroundColor": GUINDA_MATRIZ, "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px"}),
        html.Div([
            dbc.Table([
                html.Thead(html.Tr([html.Th("Descripción de la Actividad / Servicio"), html.Th("Total Acumulado", style={"textAlign": "right"})]), style={"backgroundColor": GRIS_CLARO}),
                html.Tbody(filas_tabla if filas_tabla else [html.Tr([html.Td("Sin registros", colSpan=2, className="text-center text-muted")])])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mb-0")
        ], style={"maxHeight": "380px", "overflowY": "auto", "padding": "10px"})
    ], className="bg-white border shadow-sm", style={"borderRadius": "8px"})

    # Tarjeta de Contexto Operativo
    card_info = html.Div([
        html.Div([
            html.Span("ENFOQUE DEL MÓDULO JURÍDICO", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "white"})
        ], className="p-3", style={"backgroundColor": VERDE_MATRIZ, "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px"}),
        html.Div([
            html.P("El departamento jurídico registra la atención de asesorías, representación legal, gestión de pensiones, canalizaciones a otras instancias y protección de derechos vulnerados.", style={"fontSize": "0.8rem", "color": TEXTO_DARK, "lineHeight": "1.5"}),
            html.Ul([
                html.Li("Control de atención diferenciada por género y grupos vulnerables.", style={"fontSize": "0.78rem", "color": "#4b5563"}),
                html.Li("Seguimiento a visitas domiciliarias y actas de tutela.", style={"fontSize": "0.78rem", "color": "#4b5563"}),
                html.Li(f"Volumen general acumulado en el periodo: {int(total_registros_gral):,} registros operativos.", style={"fontSize": "0.78rem", "color": "#4b5563"})
            ], className="mb-0 ps-3")
        ], style={"padding": "15px"})
    ], className="bg-white border shadow-sm h-100", style={"borderRadius": "8px"})

    return html.Div([
        kpis_row,
        dbc.Row([
            dbc.Col(tabla_consolidada, md=7, className="mb-3"),
            dbc.Col(card_info, md=5, className="mb-3")
        ])
    ])