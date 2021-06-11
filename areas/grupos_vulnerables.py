# areas/grupos_vulnerables.py
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

def analizar_grupos_vulnerables(df):
    """
    Módulo Operativo para Grupos Vulnerables adaptado exactamente con la estructura 
    institucional de tarjetas superiores, consolidado por comunidad y detalles del programa.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El DataFrame de Grupos Vulnerables llegó vacío.", color="warning", className="m-3")

    try:
        # 1. Limpieza y normalización estándar de columnas
        df_vuel = df.copy()
        df_vuel.columns = [str(c).strip().upper() for c in df_vuel.columns]

        col_comunidad = next((c for c in df_vuel.columns if "COMUNIDAD" in c), "Comunidad")
        col_beneficiarios = next((c for c in df_vuel.columns if "BENEFICIARIO" in c or "CANTIDAD" in c), "Cantidad")

        df_vuel[col_comunidad] = df_vuel[col_comunidad].astype(str).str.strip().str.title()
        df_vuel[col_beneficiarios] = pd.to_numeric(df_vuel[col_beneficiarios], errors='coerce').fillna(0)

        total_beneficiarios = df_vuel[col_beneficiarios].sum()
        
        # Análisis de comunidades atendidas frente al universo real municipal (73)
        df_efectivo = df_vuel[df_vuel[col_beneficiarios] > 0].copy()
        comunidades_atendidas = df_efectivo[col_comunidad].nunique()
        
        # Cálculo real del Índice de Cobertura Municipal
        indice_cobertura_municipal = (comunidades_atendidas / TOTAL_COMUNIDADES_MUNICIPIO * 100) if TOTAL_COMUNIDADES_MUNICIPIO > 0 else 0

        # --- TARJETAS DE RESUMEN SUPERIORES (Estructura institucional exacta) ---
        kpis_row = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("TOTAL DE CIUDADANOS ATENDIDOS", className="text-muted mb-1", style={"fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.5px"}),
                    html.H4(f"{int(total_beneficiarios):,} PERSONAS", style={"color": VERDE_MATRIZ, "fontWeight": "bold", "fontSize": "1.3rem", "marginBottom": "4px"}),
                    html.P("Acumulado histórico del periodo", className="text-muted mb-0", style={"fontSize": "0.72rem"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, md=4),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("LOCALIDADES ATENDIDAS", className="text-muted mb-1", style={"fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.5px"}),
                    html.H4(f"{comunidades_atendidas} DE {TOTAL_COMUNIDADES_MUNICIPIO}", style={"color": GUINDA_MATRIZ, "fontWeight": "bold", "fontSize": "1.3rem", "marginBottom": "4px"}),
                    html.P("Comunidades con cobertura activa", className="text-muted mb-0", style={"fontSize": "0.72rem"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {GUINDA_MATRIZ}"}), width=12, md=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("ÍNDICE DE COBERTURA MUNICIPAL", className="text-muted mb-1", style={"fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.5px"}),
                    html.H4(f"{indice_cobertura_municipal:.1f}%", style={"color": TEXTO_DARK, "fontWeight": "bold", "fontSize": "1.3rem", "marginBottom": "4px"}),
                    html.P(f"Sobre un total de {TOTAL_COMUNIDADES_MUNICIPIO} localidades", className="text-muted mb-0", style={"fontSize": "0.72rem"})
                ])
            ], className="border-0 shadow-sm mb-3", style={"borderRadius": "8px", "borderLeft": f"5px solid {VERDE_MATRIZ}"}), width=12, md=4),
        ], className="mb-3")

        # Resumen consolidado por comunidad
        df_resumen_comunidad = df_efectivo.groupby(col_comunidad)[col_beneficiarios].sum().reset_index()
        df_resumen_comunidad = df_resumen_comunidad.sort_values(by=col_beneficiarios, ascending=False)

        filas_tabla = []
        for _, row in df_resumen_comunidad.iterrows():
            filas_tabla.append(html.Tr([
                html.Td(row[col_comunidad], style={"fontSize": "0.8rem", "fontWeight": "500", "paddingLeft": "15px"}),
                html.Td(f"{int(row[col_beneficiarios]):,} personas", style={"fontSize": "0.8rem", "fontWeight": "bold", "color": VERDE_MATRIZ, "paddingRight": "15px"})
            ]))

        # Tabla con estilo de cabecera en bloque Guinda institucional
        tabla_consolidada = html.Div([
            html.Div([
                html.Span("CONSOLIDADO DE ATENCIÓN POR COMUNIDAD (ACUMULADO PERIODO)", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "white", "letterSpacing": "0.5px"})
            ], className="p-3", style={"backgroundColor": GUINDA_MATRIZ, "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px"}),
            html.Div([
                dbc.Table([
                    html.Thead(html.Tr([html.Th("COMUNIDAD / LOCALIDAD", style={"paddingLeft": "15px"}), html.Th("TOTAL ACUMULADO", style={"paddingRight": "15px"})]), style={"backgroundColor": GRIS_CLARO, "fontSize": "0.75rem", "color": "#4b5563"}),
                    html.Tbody(filas_tabla if filas_tabla else [html.Tr([html.Td("Sin registros", colSpan=2, className="text-center text-muted")])])
                ], bordered=True, hover=True, responsive=True, size="sm", className="mb-0")
            ], style={"maxHeight": "380px", "overflowY": "auto", "padding": "5px"})
        ], className="bg-white border shadow-sm", style={"borderRadius": "8px"})

        # Tarjeta de Contexto Operativo con barra superior Verde Petróleo
        card_info = html.Div([
            html.Div([
                html.Span("DETALLES DEL PROGRAMA", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "white", "letterSpacing": "0.5px"})
            ], className="p-3", style={"backgroundColor": VERDE_MATRIZ, "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px"}),
            html.Div([
                html.P("El Programa de Atención a Grupos Vulnerables opera mediante acciones continuas y entrega de apoyos orientados a beneficiarios específicos en el municipio.", style={"fontSize": "0.8rem", "color": TEXTO_DARK, "lineHeight": "1.5"}),
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

    except Exception as e:
        return dbc.Alert(f"❌ Error al estructurar el módulo de Grupos Vulnerables: {str(e)}", color="danger", className="m-3")