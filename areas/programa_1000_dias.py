import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

# Colorimetría exacta basada en la Matriz Institucional
VERDE_MATRIZ = "#115e59"      # Verde petróleo principal (Cabeceras de tabla / KPIs)
GUINDA_MATRIZ = "#691c32"     # Guinda institucional (Sub-encabezados / Líneas de acento)
TEXTO_DARK = "#1f2937"
GRIS_CLARO = "#f9fafb"

# Universo total de comunidades en el municipio
TOTAL_COMUNIDADES_MUNICIPIO = 73

def analizar_programa_1000_dias(df):
    """Módulo adaptado con tarjetas de resumen mejoradas e índice de cobertura municipal basado en las 73 comunidades totales."""
    
    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip().str.title()

    columnas_reales = df.columns.tolist()
    
    col_comunidad = next((c for c in columnas_reales if "COMUNIDAD" in str(c).upper()), "Comunidad")
    col_cantidad = next((c for c in columnas_reales if "CANTIDAD" in str(c).upper()), "Cantidad")
    col_mes = next((c for c in columnas_reales if "MES" in str(c).upper()), "Mes")

    df_limpio = pd.DataFrame()
    df_limpio['Comunidad'] = df[col_comunidad].astype(str).str.strip().str.title() if col_comunidad in df.columns else "General"
    df_limpio['Cantidad'] = pd.to_numeric(df[col_cantidad], errors='coerce').fillna(0) if col_cantidad in df.columns else 0
    df_limpio['Mes'] = df[col_mes].astype(str).str.strip().str.capitalize() if col_mes in df.columns else "General"

    total_apoyos = df_limpio['Cantidad'].sum()
    
    # Análisis de comunidades atendidas frente al universo real municipal (73)
    df_efectivo = df_limpio[df_limpio['Cantidad'] > 0].copy()
    comunidades_atendidas = df_efectivo['Comunidad'].nunique()
    
    # Cálculo real del Índice de Cobertura Municipal
    indice_cobertura_municipal = (comunidades_atendidas / TOTAL_COMUNIDADES_MUNICIPIO * 100) if TOTAL_COMUNIDADES_MUNICIPIO > 0 else 0
    meses_totales_registrados = df_efectivo['Mes'].nunique()

    # --- TARJETAS DE RESUMEN MEJORADAS ---
    kpis_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("TOTAL DE DESPENSAS ENTREGADAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_apoyos):,} apoyos", style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem"}),
                html.P("Acumulado histórico del periodo", className="text-muted mb-0", style={"fontSize": "0.7rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("LOCALIDADES ATENDIDAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{comunidades_atendidas} de {TOTAL_COMUNIDADES_MUNICIPIO}", style={"color": GUINDA_MATRIZ, "fontWeight": "bold", "fontSize": "1.2rem"}),
                html.P("Comunidades con entrega activa", className="text-muted mb-0", style={"fontSize": "0.7rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {GUINDA_MATRIZ}"}), width=12, md=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("ÍNDICE DE COBERTURA MUNICIPAL", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{indice_cobertura_municipal:.1f}%", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.2rem"}),
                html.P(f"Sobre un total de {TOTAL_COMUNIDADES_MUNICIPIO} localidades", className="text-muted mb-0", style={"fontSize": "0.7rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, md=4),
    ], className="mb-3")

    # Resumen consolidado por comunidad
    df_resumen_comunidad = df_efectivo.groupby('Comunidad')['Cantidad'].sum().reset_index()
    df_resumen_comunidad = df_resumen_comunidad.sort_values(by='Cantidad', ascending=False)

    filas_tabla = []
    for _, row in df_resumen_comunidad.iterrows():
        filas_tabla.append(html.Tr([
            html.Td(row['Comunidad'], style={"fontSize": "0.8rem", "fontWeight": "500"}),
            html.Td(f"{int(row['Cantidad']):,} despensas", style={"fontSize": "0.8rem", "fontWeight": "bold", "color": VERDE_MATRIZ})
        ]))

    # Tabla con estilo de cabecera en bloque Guinda/Verde institucional
    tabla_consolidada = html.Div([
        html.Div([
            html.Span("CONSOLIDADO DE ENTREGAS POR COMUNIDAD (ACUMULADO PERIODO)", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "white"})
        ], className="p-3", style={"backgroundColor": GUINDA_MATRIZ, "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px"}),
        html.Div([
            dbc.Table([
                html.Thead(html.Tr([html.Th("Comunidad / Localidad"), html.Th("Total Acumulado")]), style={"backgroundColor": GRIS_CLARO}),
                html.Tbody(filas_tabla if filas_tabla else [html.Tr([html.Td("Sin registros", colSpan=2, className="text-center text-muted")])])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mb-0")
        ], style={"maxHeight": "380px", "overflowY": "auto", "padding": "10px"})
    ], className="bg-white border shadow-sm", style={"borderRadius": "8px"})

    # Tarjeta de Contexto Operativo con barra superior Guinda
    card_info = html.Div([
        html.Div([
            html.Span("DETALLES DEL PROGRAMA", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "white"})
        ], className="p-3", style={"backgroundColor": VERDE_MATRIZ, "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px"}),
        html.Div([
            html.P("El Programa 1000 Días opera mediante la entrega continua de despensas destinadas a beneficiarios específicos en periodos establecidos.", style={"fontSize": "0.8rem", "color": TEXTO_DARK, "lineHeight": "1.5"}),
            html.Ul([
                html.Li(f"Universo total municipal: {TOTAL_COMUNIDADES_MUNICIPIO} localidades registradas.", style={"fontSize": "0.78rem", "color": "#4b5563"}),
                html.Li(f"Localidades atendidas efectivamente: {comunidades_atendidas}.", style={"fontSize": "0.78rem", "color": "#4b5563"}),
                html.Li(f"Localidades pendientes de cobertura: {TOTAL_COMUNIDADES_MUNICIPIO - comunidades_atendidas}.", style={"fontSize": "0.78rem", "color": "#4b5563"})
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