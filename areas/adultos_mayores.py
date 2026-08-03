import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

# Paleta institucional gubernamental unificada
TURQUESA_GOB = "#178983"   # Color principal superior (Encabezados y barra superior)
GUINDA_GOB = "#6b233a"     # Color secundario oscuro (Sub-cabeceras y detalles)
DORADO_INST = "#bc955c"    # Acento complementario
TEXTO_DARK = "#1f2937"
GRIS_FONDO_TH = "#f8fafc"

def analizar_adultos_mayores(df):
    """Análisis estructurado y ejecutivo para DIF Atención a Adultos Mayores con métricas de impacto optimizadas."""
    
    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip().str.title()

    columnas_reales = df.columns.tolist()
    
    col_actividad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["ACTIVIDAD", "CONCEPTO"])), columnas_reales[2] if len(columnas_reales) > 2 else None)
    col_beneficiarios = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["BENEF", "PERSONAS"])), None)
    col_edad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["EDAD"])), None)
    col_visitas = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["VISITAS", "SEMANA"])), None)
    col_comunidad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["COMUNIDAD", "LOCALIDAD"])), None)

    if not col_actividad:
        return dbc.Alert("⚠️ No se encontró una columna de actividad válida para Adultos Mayores.", color="danger", className="m-3")

    df_limpio = pd.DataFrame()
    df_limpio['Actividad'] = df[col_actividad].astype(str).str.strip().str.title()
    df_limpio['Comunidad'] = df[col_comunidad].astype(str).str.strip().str.title() if col_comunidad else "General"
    df_limpio['Beneficiarios'] = pd.to_numeric(df[col_beneficiarios], errors='coerce').fillna(1) if col_beneficiarios else 1
    df_limpio['Edad'] = pd.to_numeric(df[col_edad], errors='coerce').fillna(0) if col_edad else 0
    df_limpio['Visitas'] = pd.to_numeric(df[col_visitas], errors='coerce').fillna(1) if col_visitas else 1

    total_acciones = len(df_limpio)
    total_comunidades = df_limpio['Comunidad'].nunique()
    
    # Métrica alternativa de impacto: Máxima edad atendida (testimonio de cobertura integral a longevos)
    edad_maxima = df_limpio['Edad'].max() if len(df_limpio) > 0 else 0

    # --- KPI CARDS SUPERIORES (Ajustadas a 2 tarjetas de alto impacto o distribuidas) ---
    kpis_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("TOTAL DE ACCIONES / SERVICIOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{total_acciones:,} apoyos", style={"color": TURQUESA_GOB, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {TURQUESA_GOB}"}), width=12, md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("EDAD MÁXIMA ATENDIDA", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(edad_maxima)} años", style={"color": GUINDA_GOB, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {GUINDA_GOB}"}), width=12, md=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("COMUNIDADES COBERTURADAS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{total_comunidades} localidades", style={"color": DORADO_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {DORADO_INST}"}), width=12, md=4),
    ], className="mb-3")

    # Agrupación general por Actividad (Sustituyendo edad promedio por Max Visitas o Rango)
    df_grouped = df_limpio.groupby('Actividad').agg(
        Atenciones=('Beneficiarios', 'count'),
        Max_Visitas=('Visitas', 'max'),
        Visitas_Promedio=('Visitas', 'mean')
    ).reset_index()

    df_grouped['Porcentaje'] = (df_grouped['Atenciones'] / total_acciones * 100) if total_acciones > 0 else 0
    df_grouped = df_grouped.sort_values(by='Atenciones', ascending=False).reset_index(drop=True)

    # --- TABLA EJECUTIVA OPTIMIZADA ---
    filas_tabla = []
    for _, row in df_grouped.iterrows():
        pct = row['Porcentaje']
        filas_tabla.append(
            html.Tr([
                html.Td([
                    html.Div(row['Actividad'], style={"fontWeight": "600", "color": TEXTO_DARK, "fontSize": "0.85rem"}),
                    html.Div(
                        dbc.Progress(
                            value=pct, 
                            style={"height": "4px", "marginTop": "4px", "backgroundColor": "#e5e7eb"}, 
                            className="w-100",
                            color="success"
                        )
                    )
                ], style={"width": "35%"}),
                html.Td(f"{int(row['Atenciones']):,}", className="text-center align-middle", style={"fontSize": "0.85rem"}),
                html.Td(f"{row['Visitas_Promedio']:.1f} por sem.", className="text-center align-middle", style={"fontSize": "0.85rem"}),
                html.Td(f"{int(row['Max_Visitas'])} máx.", className="text-center align-middle", style={"fontSize": "0.85rem"}),
                html.Td(f"{pct:.1f}%", className="text-center align-middle", style={"fontSize": "0.85rem", "fontWeight": "600", "color": GUINDA_GOB})
            ])
        )

    tabla_ejecutiva = html.Div([
        html.Div([
            # Franja superior turquesa institucional
            html.Div(style={"backgroundColor": TURQUESA_GOB, "height": "6px", "borderTopLeftRadius": "14px", "borderTopRightRadius": "14px"}),
            html.Div([
                # Título con fondo guinda
                html.Div([
                    html.Span("SÍNTESIS CONSOLIDADA - ATENCIÓN A ADULTOS MAYORES", style={"color": "white", "fontWeight": "bold", "fontSize": "0.85rem", "letterSpacing": "0.5px"})
                ], style={"backgroundColor": GUINDA_GOB, "padding": "10px 15px", "borderRadius": "6px", "marginBottom": "15px"}),
                
                dbc.Table([
                    html.Thead(
                        html.Tr([
                            html.Th("Rubro / Actividad"),
                            html.Th("Total Atenciones", className="text-center"),
                            html.Th("Frecuencia Promedio", className="text-center"),
                            html.Th("Frecuencia Máxima", className="text-center"),
                            html.Th("Participación", className="text-center"),
                        ], style={"backgroundColor": GRIS_FONDO_TH, "color": TEXTO_DARK, "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "0.5px"})
                    ),
                    html.Tbody(filas_tabla)
                ], bordered=False, hover=True, responsive=True, className="align-middle mb-0")
            ], style={"padding": "15px 20px 20px 20px"})
        ], className="bg-white border shadow-sm mb-4", style={"borderRadius": "14px"})
    ])

    return html.Div([
        kpis_row,
        tabla_ejecutiva
    ])