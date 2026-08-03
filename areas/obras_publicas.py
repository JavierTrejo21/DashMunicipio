# areas/obras_publicas.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, callback, State
import json

# Colorimetría institucional unificada (Guinda y Dorado predominantes)
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
TEXTO_DARK = "#1f2937"
TEXTO_SECUNDARIO = "#374151"

def analizar_obras_publicas(df):
    if df is None or df.empty:
        return dbc.Alert("⚠️ El archivo de Obras Públicas no contiene registros válidos.", color="warning")

    df_op = df.copy()
    df_op.columns = [str(c).strip().upper() for c in df_op.columns]
    columnas_reales = df_op.columns.tolist()
    
    # Identificación segura de columnas
    col_tipo = next((c for c in columnas_reales if "TIPO" in c or "RUBRO" in c), "TIPO DE OBRA")
    col_benef = next((c for c in columnas_reales if "BENEF" in c or "ATEND" in c), "BENEFICIARIOS")
    col_inv = next((c for c in columnas_reales if "INV" in c), "INVERSION")
    col_comunidad = next((c for c in columnas_reales if "COMUNIDAD" in c or "LOC" in c), "COMUNIDAD")
    col_categoria = next((c for c in columnas_reales if "CAT" in c), "CATEGORIA")
    col_proyecto = next((c for c in columnas_reales if "PROYECTO" in c or "ACCION" in c), "PROYECTO REALIZADO")
    col_ubicacion = next((c for c in columnas_reales if "UBIC" in c), "UBICACIÓN")

    # Limpieza numérica de beneficiarios
    if col_benef in df_op.columns:
        df_op[col_benef] = pd.to_numeric(df_op[col_benef], errors='coerce').fillna(0)
    else:
        df_op['BENEFICIARIOS'] = 0
        col_benef = 'BENEFICIARIOS'

    # Limpieza numérica de inversión
    if col_inv in df_op.columns:
        df_op[col_inv] = df_op[col_inv].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
        df_op[col_inv] = pd.to_numeric(df_op[col_inv], errors='coerce').fillna(0)
    else:
        df_op['INVERSION'] = 0
        col_inv = 'INVERSION'

    # Extracción de coordenadas limpias para cada registro
    latitudes = []
    longitudes = []
    links_mapa = []
    
    for _, row in df_op.iterrows():
        val_ubicacion = str(row.get(col_ubicacion, "")).strip()
        lat, lon = 21.155597, -98.903757 # Centro por defecto (Chapulhuacán Centro)
        if val_ubicacion and "," in val_ubicacion:
            try:
                partes = val_ubicacion.split(",")
                lat = float(partes[0].strip())
                lon = float(partes[1].strip())
            except Exception:
                pass
        latitudes.append(lat)
        longitudes.append(lon)
        links_mapa.append("📍 Ver en Mapa" if (val_ubicacion and "," in val_ubicacion) else "Sin georreferencia")

    df_op['LAT_MAP'] = latitudes
    df_op['LON_MAP'] = longitudes
    df_op['UBICACION_MAPA_BTN'] = links_mapa

    # Separación por categoría (FAISM / Obras vs Campo / Asesorías)
    if col_categoria in df_op.columns:
        df_faism = df_op[df_op[col_categoria].astype(str).str.upper().str.contains("FAISM|OBRA|GESTION", na=False)].copy()
        df_campo = df_op[df_op[col_categoria].astype(str).str.upper().str.contains("CAMPO|ASESORIA|ACTIVIDAD", na=False)].copy()
    else:
        df_faism = df_op.copy()
        df_campo = pd.DataFrame(columns=df_op.columns)

    if df_faism.empty:
        df_faism = df_op.copy()

    total_obras = len(df_faism)
    total_inversion = df_faism[col_inv].sum()
    total_beneficiarios = df_faism[col_benef].sum()
    total_actividades_secundarias = len(df_campo)

    # Columnas para tablas interactivas
    columnas_tabla_faism = [
        {"name": "Proyecto / Obra realizada", "id": col_proyecto},
        {"name": "Localidad / Comunidad", "id": col_comunidad},
        {"name": "Rubro Técnico", "id": col_tipo},
        {"name": "Beneficiarios", "id": col_benef},
        {"name": "Ubicación Mapas", "id": "UBICACION_MAPA_BTN"}
    ]
    if col_inv in df_faism.columns:
        df_faism["INVERSIÓN FORMATEADA"] = df_faism[col_inv].apply(lambda x: f"${x:,.2f}")
        columnas_tabla_faism.insert(3, {"name": "Monto Autorizado", "id": "INVERSIÓN FORMATEADA"})

    columnas_tabla_campo = [
        {"name": "Acción / Reporte", "id": col_proyecto},
        {"name": "Localidad Atendida", "id": col_comunidad},
        {"name": "Tipo de Actividad", "id": col_tipo},
        {"name": "Ciudadanos Atendidos", "id": col_benef},
        {"name": "Ubicación Mapas", "id": "UBICACION_MAPA_BTN"}
    ]

    estilo_kpi = {
        "borderRadius": "8px", 
        "cursor": "pointer",
        "transition": "all 0.25s ease-in-out"
    }

    tarjetas_kpi = dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": GUINDA_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("OBRAS EN EJECUCIÓN (FAISM) 🖱️", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{total_obras} Proyectos", className="m-0 font-weight-bold mt-1", style={"color": TEXTO_DARK, "fontSize": "1.25rem"}),
                html.Small("Ver registros relacionados", className="d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px", "color": GUINDA_INST})
            ], id="kpi-obras-click", className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": DORADO_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("INVERSIÓN TOTAL AUTORIZADA", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"${total_inversion:,.2f}", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": GUINDA_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("POBLACIÓN BENEFICIADA", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{total_beneficiarios:,.0f} habs.", className="m-0 font-weight-bold mt-1", style={"color": TEXTO_DARK, "fontSize": "1.25rem"})
            ], className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
        dbc.Col(
            html.Div([
                html.Div(style={"position": "absolute", "top": "0", "left": "0", "bottom": "0", "width": "5px", "backgroundColor": DORADO_INST, "borderRadius": "8px 0 0 8px"}),
                html.Small("ASESORÍAS Y TRABAJOS DE CAMPO 🖱️", className="font-weight-bold d-block", style={"fontSize": "0.68rem", "letterSpacing": "0.5px", "color": TEXTO_SECUNDARIO}),
                html.H3(f"{total_actividades_secundarias} Acciones", className="m-0 font-weight-bold mt-1", style={"color": GUINDA_INST, "fontSize": "1.25rem"}),
                html.Small("Ver registros relacionados", className="d-block font-weight-bold", style={"fontSize": "0.58rem", "marginTop": "3px", "color": DORADO_INST})
            ], id="kpi-asesorias-click", className="bg-white border p-3 position-relative shadow-sm h-100", style=estilo_kpi), width=12, sm=6, md=3, className="mb-3"
        ),
    ], className="mb-2")

    desplegable_obras = dbc.Collapse(
        html.Div([
            html.Div([
                html.I(className="bi bi-table me-2"), "REGISTROS INTERNOS: PROYECTOS DE INFRAESTRUCTURA (FAISM)"
            ], style={"backgroundColor": GUINDA_INST, "color": "white", "padding": "8px 12px", "fontWeight": "bold", "fontSize": "0.75rem", "borderRadius": "6px 6px 0 0"}),
            html.Div([
                dash_table.DataTable(
                    id='tabla-obras-faism',
                    data=df_faism.to_dict('records'),
                    columns=columnas_tabla_faism,
                    page_size=5,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'color': TEXTO_DARK, 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'},
                    style_cell={'padding': '10px 8px', 'fontSize': '11px', 'fontFamily': 'sans-serif', 'textAlign': 'left', 'borderBottom': '1px solid #f9fafb', 'color': TEXTO_DARK},
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'},
                        {'if': {'column_id': 'UBICACION_MAPA_BTN'}, 'color': GUINDA_INST, 'fontWeight': 'bold', 'cursor': 'pointer'}
                    ]
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
            ], style={"backgroundColor": GUINDA_INST, "color": "white", "padding": "8px 12px", "fontWeight": "bold", "fontSize": "0.75rem", "borderRadius": "6px 6px 0 0"}),
            html.Div([
                dash_table.DataTable(
                    id='tabla-obras-campo',
                    data=df_campo.to_dict('records'),
                    columns=columnas_tabla_campo,
                    page_size=5,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'color': TEXTO_DARK, 'fontWeight': 'bold', 'fontSize': '11px', 'textAlign': 'left', 'borderBottom': '2px solid #e5e7eb'},
                    style_cell={'padding': '10px 8px', 'fontSize': '11px', 'fontFamily': 'sans-serif', 'textAlign': 'left', 'borderBottom': '1px solid #f9fafb', 'color': TEXTO_DARK},
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'},
                        {'if': {'column_id': 'UBICACION_MAPA_BTN'}, 'color': GUINDA_INST, 'fontWeight': 'bold', 'cursor': 'pointer'}
                    ]
                )
            ], className="border border-top-0 p-2 bg-white", style={"borderRadius": "0 0 6px 6px"})
        ], className="mb-3 shadow-sm"),
        id="collapse-tabla-asesorias",
        is_open=False,
    )

    puntos_google_maps = []
    for _, row in df_op.iterrows():
        puntos_google_maps.append({
            "lat": row['LAT_MAP'],
            "lng": row['LON_MAP'],
            "titulo": str(row.get(col_proyecto, "Obra Municipal")).strip(),
            "comunidad": str(row.get(col_comunidad, "LOCALIDAD")).strip().upper(),
            "rubro": str(row.get(col_tipo, "GENERAL")).strip().upper(),
            "inversion": f"${row.get(col_inv, 0):,.2f}",
            "beneficiarios": str(row.get(col_benef, 0))
        })

    return html.Div([
        dcc.Store(id='store-mapa-seleccion', data={
            "lat": 21.155597, 
            "lng": -98.903757, 
            "zoom": 11.2, 
            "titulo": "",
            "puntos": puntos_google_maps
        }),
        tarjetas_kpi,
        desplegable_obras,
        desplegable_asesorias,
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    html.I(className="bi bi-map-fill me-2", style={"color": DORADO_INST}), 
                    "VISOR GEOGRÁFICO INTERACTIVO DE OBRAS Y ACCIONES"
                ], style={'backgroundColor': GUINDA_INST, 'color': 'white', 'padding': '12px 16px', 'fontWeight': '700', 'fontSize': '0.75rem', 'borderRadius': '6px 6px 0 0'}),
                html.Iframe(
                    id='iframe-mapa-obras',
                    srcDoc="", 
                    width="100%",
                    height="520",
                    style={"border": "0", "borderRadius": "0 0 6px 6px"}
                )
            ], className="bg-white border shadow-sm mb-3", style={'borderRadius': '6px'}), md=12)
        ])
    ], style={'padding': '5px'})


# =============================================================================
# CALLBACKS DE CONTROL Y ACTUALIZACIÓN DEL MAPA
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


@callback(
    Output("store-mapa-seleccion", "data"),
    [Input("tabla-obras-faism", "active_cell"),
     Input("tabla-obras-campo", "active_cell")],
    [State("tabla-obras-faism", "data"),
     State("tabla-obras-campo", "data"),
     State("store-mapa-seleccion", "data")],
    prevent_initial_call=True
)
def capturar_clic_ubicacion(active_cell_faism, active_cell_campo, data_faism, data_campo, current_store):
    from dash import callback_context
    if not callback_context.triggered:
        return dash.no_update
    
    trig_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    cell = active_cell_faism if trig_id == "tabla-obras-faism" else active_cell_campo
    dataset = data_faism if trig_id == "tabla-obras-faism" else data_campo

    if not cell or not dataset:
        return dash.no_update

    if cell.get("column_id") == "UBICACION_MAPA_BTN":
        row_idx = cell.get("row")
        if row_idx is not None and 0 <= row_idx < len(dataset):
            row_data = dataset[row_idx]
            puntos_actuales = current_store.get("puntos", []) if current_store else []
            return {
                "lat": float(row_data.get("LAT_MAP", 21.155597)),
                "lng": float(row_data.get("LON_MAP", -98.903757)),
                "zoom": 17,
                "titulo": str(row_data.get("PROYECTO REALIZADO", row_data.get("ACCIÓN / REPORTE", ""))),
                "puntos": puntos_actuales
            }
            
    return dash.no_update


@callback(
    Output("iframe-mapa-obras", "srcDoc"),
    Input("store-mapa-seleccion", "data")
)
def actualizar_mapa_html(sel_data):
    if not sel_data:
        return ""
    
    target_lat = sel_data.get("lat", 21.155597)
    target_lng = sel_data.get("lng", -98.903757)
    target_zoom = sel_data.get("zoom", 11.2)
    target_titulo = sel_data.get("titulo", "")
    puntos = sel_data.get("puntos", [])

    puntos_json = json.dumps(puntos)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        html, body, #map {{ height: 100%; margin: 0; padding: 0; font-family: sans-serif; }}
        .custom-popup {{ font-size: 12px; }}
        .legend {{
            background: white;
            padding: 10px 14px;
            font: 11px/16px Arial, Helvetica, sans-serif;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 6px;
            color: #1f2937;
            max-width: 200px;
        }}
        .legend h4 {{
            margin: 0 0 6px 0;
            font-size: 12px;
            font-weight: bold;
            color: #691c32;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 4px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 4px;
            font-size: 11px;
        }}
        .legend i {{
            width: 12px;
            height: 12px;
            flex-shrink: 0;
            margin-right: 8px;
            border-radius: 50%;
            border: 1px solid #fff;
            box-shadow: 0 0 2px rgba(0,0,0,0.3);
        }}
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
    <div id="map" style="width: 100%; height: 100%;"></div>
    <script>
        var map = L.map('map', {{
            minZoom: 11,
            maxZoom: 19
        }}).setView([{target_lat}, {target_lng}], {target_zoom});
        
        L.tileLayer('https://{{s}}.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            subdomains:['mt0','mt1','mt2','mt3'],
            attribution: '&copy; Google Maps'
        }}).addTo(map);

        function getColor(rubro) {{
            var r = (rubro || "").toUpperCase();
            if (r.includes("VIAL")) return "#115e59";
            if (r.includes("HIDR") || r.includes("AGUA")) return "#14b8a6";
            if (r.includes("SANIT") || r.includes("DREN")) return "#d97706";
            if (r.includes("CONTEN")) return "#bc955c";
            if (r.includes("PLUV")) return "#2563eb";
            if (r.includes("EDIF")) return "#ea580c";
            if (r.includes("URB")) return "#9333ea";
            if (r.includes("EDUC")) return "#691c32";
            return "#374151";
        }}

        var legend = L.control({{position: 'topright'}});
        legend.onAdd = function (map) {{
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<h4>Rubros y Colores</h4>' +
                '<div class="legend-item"><i style="background:#115e59"></i>Vialidades</div>' +
                '<div class="legend-item"><i style="background:#14b8a6"></i>Hidráulica / Agua</div>' +
                '<div class="legend-item"><i style="background:#d97706"></i>Sanitario / Drenaje</div>' +
                '<div class="legend-item"><i style="background:#bc955c"></i>Contención</div>' +
                '<div class="legend-item"><i style="background:#2563eb"></i>Pluvial</div>' +
                '<div class="legend-item"><i style="background:#ea580c"></i>Edificación</div>' +
                '<div class="legend-item"><i style="background:#9333ea"></i>Urbanización</div>' +
                '<div class="legend-item"><i style="background:#691c32"></i>Educativa</div>' +
                '<div class="legend-item"><i style="background:#374151"></i>General / Otro</div>';
            return div;
        }};
        legend.addTo(map);

        var puntos = {puntos_json};
        var markersGroup = L.layerGroup().addTo(map);
        var targetMarker = null;

        puntos.forEach(function(p) {{
            if (p.lat && p.lng) {{
                var colorMark = getColor(p.rubro);
                var marker = L.circleMarker([p.lat, p.lng], {{
                    radius: 7,
                    fillColor: colorMark,
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.85
                }});

                var popupContent = '<div class="custom-popup">' +
                    '<b>' + p.titulo + '</b><br>' +
                    '<b>Localidad:</b> ' + p.comunidad + '<br>' +
                    '<b>Rubro:</b> ' + p.rubro + '<br>' +
                    '<b>Inversión:</b> ' + p.inversion + '<br>' +
                    '<b>Beneficiarios:</b> ' + p.beneficiarios +
                    '</div>';

                marker.bindPopup(popupContent);
                marker.addTo(markersGroup);

                if ("{target_titulo}" !== "" && p.titulo === "{target_titulo}" && Math.abs(p.lat - {target_lat}) < 0.0001) {{
                    targetMarker = marker;
                }}
            }}
        }});

        var targetLat = {target_lat};
        var targetLng = {target_lng};
        var targetZoom = {target_zoom};

        if (targetZoom > 12) {{
            map.flyTo([targetLat, targetLng], targetZoom, {{ duration: 0.8 }});
            if (targetMarker) {{
                setTimeout(function() {{
                    targetMarker.openPopup();
                }}, 700);
            }}
        }}
    </script>
</body>
</html>"""