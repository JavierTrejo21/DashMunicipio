import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

# Paleta institucional basada en la referencia gubernamental
TURQUESA_GOB = "#178983"   # Color principal superior (Encabezados y barra superior)
GUINDA_GOB = "#6b233a"     # Color secundario oscuro (Sub-cabeceras y detalles)
DORADO_INST = "#bc955c"    # Acento complementario
TEXTO_DARK = "#1f2937"
GRIS_FONDO_TH = "#f8fafc"

def analizar_apoyos_economicos(df):
    """Análisis estructurado y ejecutivo para DIF Apoyos Económicos con colorimetría gubernamental."""
    
    if df is not None and not df.empty:
        df = df.dropna(how='all')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()

    columnas_reales = df.columns.tolist()
    
    col_actividad = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["ACTIVIDAD", "CAT", "APOYO", "CONCEPTO"])), columnas_reales[0] if columnas_reales else None)
    col_inversion = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["INV", "COSTO", "MONTO", "IMPORTE"])), None)
    col_beneficiarios = next((c for c in columnas_reales if any(k in str(c).upper() for k in ["BENEF", "PERSONAS", "POBLACION"])), None)

    if not col_actividad:
        return dbc.Alert("⚠️ No se encontró una columna de actividad válida para Apoyos Económicos.", color="danger", className="m-3")

    df_limpio = pd.DataFrame()
    df_limpio['Actividad'] = df[col_actividad].astype(str).str.strip().str.title()
    
    if col_inversion:
        serie_inv = df[col_inversion].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
        serie_inv = serie_inv.replace(['-', ''], '0')
        df_limpio['Inversión'] = pd.to_numeric(serie_inv, errors='coerce').fillna(0)
    else:
        df_limpio['Inversión'] = 0

    df_limpio['Beneficiarios'] = pd.to_numeric(df[col_beneficiarios], errors='coerce').fillna(0) if col_beneficiarios else 0

    df_limpio = df_limpio[
        (df_limpio['Actividad'] != '') & 
        (df_limpio['Actividad'] != 'Nan')
    ]

    total_inversion = df_limpio['Inversión'].sum()
    total_beneficiarios = df_limpio['Beneficiarios'].sum()

    # --- KPI CARDS SUPERIORES ---
    kpis_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("INVERSIÓN TOTAL EN APOYOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"${total_inversion:,.2f}", style={"color": TURQUESA_GOB, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {TURQUESA_GOB}"}), width=12, md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("TOTAL DE BENEFICIARIOS", className="text-muted mb-1", style={"fontSize": "0.7rem", "fontWeight": "700"}),
                html.H4(f"{int(total_beneficiarios):,} personas", style={"color": DORADO_INST, "fontWeight": "bold", "fontSize": "1.1rem"})
            ])
        ], className="border-0 shadow-sm mb-3", style={"borderRadius": "12px", "borderLeft": f"4px solid {DORADO_INST}"}), width=12, md=6),
    ], className="mb-3")

    # Agrupación general por Actividad
    df_grouped = df_limpio.groupby('Actividad').agg({'Inversión': 'sum', 'Beneficiarios': 'sum'}).reset_index()
    df_grouped['Porcentaje'] = (df_grouped['Inversión'] / total_inversion * 100) if total_inversion > 0 else 0
    df_grouped = df_grouped.sort_values(by='Inversión', ascending=False).reset_index(drop=True)

    # --- TABLA EJECUTIVA CON COLORIMETRÍA GUBERNAMENTAL ---
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
                            # Usamos un color nativo compatible de bootstrap o inyectamos color vía className/estilo interno
                            color="success"
                        )
                    )
                ], style={"width": "40%"}),
                html.Td(f"{int(row['Beneficiarios']):,}", className="text-center align-middle", style={"fontSize": "0.85rem"}),
                html.Td(f"${row['Inversión']:,.2f}", className="text-end align-middle", style={"fontWeight": "bold", "color": TURQUESA_GOB, "fontSize": "0.85rem"}),
                html.Td(f"{pct:.1f}%", className="text-center align-middle", style={"fontSize": "0.85rem", "fontWeight": "600", "color": GUINDA_GOB})
            ])
        )

    tabla_ejecutiva = html.Div([
        html.Div([
            # Franja superior turquesa idéntica al estilo de la referencia
            html.Div(style={"backgroundColor": TURQUESA_GOB, "height": "6px", "borderTopLeftRadius": "14px", "borderTopRightRadius": "14px"}),
            html.Div([
                # Título estilo bloque institucional con fondo guinda
                html.Div([
                    html.Span("SÍNTESIS CONSOLIDADA DE APOYOS ECONÓMICOS", style={"color": "white", "fontWeight": "bold", "fontSize": "0.85rem", "letterSpacing": "0.5px"})
                ], style={"backgroundColor": GUINDA_GOB, "padding": "10px 15px", "borderRadius": "6px", "marginBottom": "15px"}),
                
                dbc.Table([
                    html.Thead(
                        html.Tr([
                            html.Th("Rubro / Actividad"),
                            html.Th("Beneficiarios", className="text-center"),
                            html.Th("Inversión Total", className="text-end"),
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