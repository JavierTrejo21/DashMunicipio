# areas/obras_publicas.py
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, callback, State  # <-- SOLUCIONADO: 'State' importado correctamente

# =============================================================================
# COORDENADAS PRECISAS DE LAS COMUNIDADES DE CHAPULHUACÁN
# =============================================================================
COORDENADAS_COMUNIDADES = {
    "CHAPULHUACAN": {"lat": 21.1554, "lon": -98.9048},
    "AHUAYO": {"lat": 21.1412, "lon": -98.9215},
    "AMIXCO": {"lat": 21.1325, "lon": -98.8872},
    "ARROYO BLANCO": {"lat": 21.1731, "lon": -98.9324},
    "ARROYO DE ACAXTLA": {"lat": 21.1610, "lon": -98.8920},
    "CAHUAZAS": {"lat": 21.1189, "lon": -98.9416},
    "REFORMA DE PALO SEMITA": {"lat": 21.1850, "lon": -98.9112},
    "SAN RAFAEL": {"lat": 21.1492, "lon": -98.8643},
    "SANTA ANA DE ALLENDE": {"lat": 21.2014, "lon": -98.8956},
    "SANTA MARIA DE ALAMOS": {"lat": 21.1042, "lon": -98.9011},
    "SOLEDAD DEL COYOL": {"lat": 21.1925, "lon": -98.9489},
}

def analizar_obras_publicas(df):
    """
    Módulo analítico premium individualizado para Obras Públicas.
    Filtra inversión, procesa las categorías de FAISM vs Campo,
    y genera las estructuras de las tablas desplegables interactivas.
    """
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Obras Públicas no contiene registros válidos.", color="warning")

    # --- HOMOLOGAR EN MAYÚSCULAS ---
    df_op = df.copy()
    df_op.columns = [str(c).strip().upper() for c in df_op.columns]
    columnas_reales = df_op.columns.tolist()
    
    col_tipo = next((c for c in columnas_reales if "TIPO" in c or "RUBRO" in c), None)
    col_benef = next((c for c in columnas_reales if "BENEF" in c or "ATEND" in c), None)
    col_inv = next((c for c in columnas_reales if "INV" in c), None)
    col_comunidad = next((c for c in columnas_reales if "COMUNIDAD" in c or "LOC" in c), None)
    col_categoria = next((c for c in columnas_reales if "CAT" in c), None)
    col_proyecto = next((c for c in columnas_reales if "PROYECTO" in c or "ACCION" in c), None)

    # --- LIMPIEZA RIGUROSA Y FORMATEO DE MONTO ---
    if col_benef:
        df_op[col_benef] = pd.to_numeric(df_op[col_benef], errors='coerce').fillna(0)
    else:
        df_op['BENEFICIARIOS'] = 0
        col_benef = 'BENEFICIARIOS'

    if col_inv:
        df_op[col_inv] = df_op[col_inv].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
        df_op[col_inv] = pd.to_numeric(df_op[col_inv], errors='coerce').fillna(0)
    else:
        df_op['INVERSION'] = 0
        col_inv = 'INVERSION'

    # --- SEGMENTACIÓN MUNICIPAL DE DATOS ---
    if col_categoria:
        df_faism = df_op[df_op[col_categoria].astype(str).str.upper().str.contains("FAISM|OBRA|GESTION", na=False)].copy()
        df_campo = df_op[df_op[col_categoria].astype(str).str.upper().str.contains("CAMPO|ASESORIA|ACTIVIDAD", na=False)].copy()
    else:
        df_faism = df_op[df_op[col_inv] > 0].copy()
        df_campo = df_op[df_op[col_inv] == 0].copy()

    if df_faism.empty:
        df_faism = df_op[df_op[col_inv] > 0].copy()

    total_obras = len(df_faism)
    total_inversion = df_faism[col_inv].sum()
    total_beneficiarios = df_faism[col_benef].sum()
    total_actividades_secundarias = len(df_campo)

    # Columnas para las tablas (renombradas visualmente para la interfaz)
    columnas_tabla_faism = [
        {"name": "Proyecto / Obra realizada", "id": col_proyecto},
        {"name": "Localidad / Comunidad", "id": col_comunidad},
        {"name": "Rubro Técnico", "id": col_tipo},
        {"name": "Beneficiarios", "id": col_benef}
    ]
    if col_inv:
        df_faism["INVERSIÓN FORMATEADA"] = df_faism[col_inv].apply(lambda x: f"${x:,.2f}")
        columnas_tabla_faism.append({"name": "Monto Autorizado", "id": "INVERSIÓN FORMATEADA"})

    columnas_tabla_campo = [
        {"name": "Acción / Reporte", "id": col_proyecto},
        {"name": "Localidad Atendida", "id": col_comunidad},
        {"name": "Tipo de Actividad", "id": col_tipo},
        {"name": "Ciudadanos Atendidos", "id": col_benef}
    ]

    # --- TABLERO DE TARJETAS (KPIs) ---
    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#691c32", "borderRadius": "8px 0 0 8px"}),
                html.Small("OBRAS EN EJECUCIÓN (FAISM) 🖱️", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{total_obras} Proyectos", className="m-0 font-weight-bold mt-1", style={"color": "#1f2937", "fontSize": "1.25rem"}),
                html.Small("Ver registros relacionados", className="text-primary d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px"})
            ], id="kpi-obras-click", className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px", "cursor": "pointer"}), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#bc955c", "borderRadius": "8px 0 0 8px"}),
                html.Small("INVERSIÓN TOTAL AUTORIZADA", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"${total_inversion:,.2f}", className="m-0 font-weight-bold mt-1", style={"color": "#691c32", "fontSize": "1.25rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#2563eb", "borderRadius": "8px 0 0 8px"}),
                html.Small("POBLACIÓN BENEFICIADA", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{total_beneficiarios:,.0f} habs.", className="m-0 font-weight-bold mt-1", style={"color": "#1f2937", "fontSize": "1.25rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px"}), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": "#10b981", "borderRadius": "8px 0 0 8px"}),
                html.Small("ASESORÍAS Y TRABAJOS DE CAMPO 🖱️", className="text-muted font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px"}),
                html.H3(f"{total_actividades_secundarias} Acciones", className="m-0 font-weight-bold mt-1", style={"color": "#10b981", "fontSize": "1.25rem"}),
                html.Small("Ver registros relacionados", className="text-success d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px"})
            ], id="kpi-asesorias-click", className="bg-white border p-3 position-relative shadow-sm h-100", style={"borderRadius": "8px", "cursor": "pointer"}), width=12, sm=6, md=3, className="mb-3"
        ),
    ], className="mb-2")

    # --- INTERCALADO: CONTENEDORES DESPLEGABLES (COLLAPSE) ---
    desplegable_obras = dbc.Collapse(
        html.Div([
            html.Div([
                html.I(className="bi bi-table me-2"), "REGISTROS INTERNOS: PROYECTOS DE INFRAESTRUCTURA (FAISM)"
            ], style={"backgroundColor": "#691c32", "color": "white", "padding": "8px 12px", "fontWeight": "bold", "fontSize": "0.75rem", "borderRadius": "6px 6px 0 0"}),
            html.Div([
                dash_table.DataTable(
                    data=df_faism.to_dict('records'),
                    columns=columnas_tabla_faism,
                    page_size=5,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'color': '#1f2937', 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'},
                    style_cell={'padding': '10px 8px', 'fontSize': '11px', 'fontFamily': 'sans-serif', 'textAlign': 'left', 'borderBottom': '1px solid #f3f4f6'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}]
                )
            ], className="border border-top-0 p-2 bg-white", style={"borderRadius": "0 0 6px 6px"})
        ], className="mb-3 shadow-sm"),
        id="collapse-tabla-obras",
        is_open=False,
    )

    desplegable_asesorias = dbc.Collapse(
        html.Div([
            html.Div([
                html.I(className="bi bi-table me-2"), "REGISTROS INTERNOS: LISTADO DE ASESORÍAS Y LEVANTAMIENTOS TÉCNICOS"
            ], style={"backgroundColor": "#10b981", "color": "white", "padding": "8px 12px", "fontWeight": "bold", "fontSize": "0.75rem", "borderRadius": "6px 6px 0 0"}),
            html.Div([
                dash_table.DataTable(
                    data=df_campo.to_dict('records'),
                    columns=columnas_tabla_campo,
                    page_size=5,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'color': '#1f2937', 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'},
                    style_cell={'padding': '10px 8px', 'fontSize': '11px', 'fontFamily': 'sans-serif', 'textAlign': 'left', 'borderBottom': '1px solid #f3f4f6'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}]
                )
            ], className="border border-top-0 p-2 bg-white", style={"borderRadius": "0 0 6px 6px"})
        ], className="mb-3 shadow-sm"),
        id="collapse-tabla-asesorias",
        is_open=False,
    )

    # --- CONFIGURACIÓN DEL MAPA VÍVIDO ---
    def asignar_lat(com):
        return COORDENADAS_COMUNIDADES.get(str(com).strip().upper(), COORDENADAS_COMUNIDADES["CHAPULHUACAN"])["lat"]
    def asignar_lon(com):
        return COORDENADAS_COMUNIDADES.get(str(com).strip().upper(), COORDENADAS_COMUNIDADES["CHAPULHUACAN"])["lon"]

    df_mapa_data = df_faism.copy()
    df_mapa_data["LAT"] = df_mapa_data[col_comunidad].apply(asignar_lat)
    df_mapa_data["LON"] = df_mapa_data[col_comunidad].apply(asignar_lon)
    df_mapa_data["MONTO_TEXTO"] = df_mapa_data[col_inv].apply(lambda x: f"${x:,.2f}")
    df_mapa_data["RADIO_GRAFICA"] = df_mapa_data[col_benef].apply(lambda x: x if x > 0 else 50)

    fig_mapa = px.scatter_mapbox(
        df_mapa_data, lat="LAT", lon="LON",
        color=col_tipo if col_tipo else col_comunidad,
        size="RADIO_GRAFICA", size_max=20, zoom=12.2,
        center=COORDENADAS_COMUNIDADES["CHAPULHUACAN"],
        mapbox_style="open-street-map",
        hover_name=col_comunidad,
        hover_data={"LAT": False, "LON": False, "RADIO_GRAFICA": False, col_tipo: True, col_benef: True, "MONTO_TEXTO": True},
        color_discrete_sequence=["#691c32", "#bc955c", "#1e3a8a", "#10b981", "#f59e0b"]
    )
    fig_mapa.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True, legend=dict(title_text="<b>Rubro de Obra</b>", yanchor="top", y=0.97, xanchor="left", x=0.02, bgcolor="rgba(255, 255, 255, 0.95)", bordercolor="#e5e7eb", borderwidth=1, font=dict(size=10)))
    fig_mapa.update_traces(marker=dict(opacity=0.85))

    return html.Div([
        tarjetas_kpi,
        desplegable_obras,       # Intercalado exactamente en medio
        desplegable_asesorias,   # Intercalado exactamente en medio
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([html.I(className="bi bi-map-fill me-2", style={"color": "#bc955c"}), "INFRAESTRUCTURA URBANA Y ACCIONES DE OBRA PÚBLICA EN CHAPULHUACÁN"], style={'backgroundColor': '#1f2937', 'color': 'white', 'padding': '12px 16px', 'fontWeight': '700', 'fontSize': '0.8rem', 'borderRadius': '6px 6px 0 0'}),
                html.Div(dcc.Graph(figure=fig_mapa, config={'displayModeBar': True, 'scrollZoom': True}), style={'padding': '0px'})
            ], className="bg-white border shadow-sm", style={'borderRadius': '6px'}), md=12)
        ])
    ], style={'padding': '5px'})


# =============================================================================
# CALLBACKS INTERACTIVOS LOCALES (MECANISMO DE CLIC PARA DESPLEGAR/OCULTAR)
# =============================================================================
@callback(
    Output("collapse-tabla-obras", "is_open"),
    Input("kpi-obras-click", "n_clicks"),
    State("collapse-tabla-obras", "is_open"),
    prevent_initial_call=True
)
def alternar_desplegable_obras(n_clicks, estado_actual):
    if n_clicks:
        return not estado_actual
    return estado_actual


@callback(
    Output("collapse-tabla-asesorias", "is_open"),
    Input("kpi-asesorias-click", "n_clicks"),
    State("collapse-tabla-asesorias", "is_open"),
    prevent_initial_call=True
)
def alternar_desplegable_asesorias(n_clicks, estado_actual):
    if n_clicks:
        return not estado_actual
    return estado_actual
