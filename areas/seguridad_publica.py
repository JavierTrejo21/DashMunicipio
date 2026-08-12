import json
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dash_table, dcc, html
import pandas as pd

VERDE_PRINCIPAL = "#0f4c3a"
GUINDA_INST = "#691c32"
DORADO_INST = "#bc955c"
TEXTO_DARK = "#1f2937"
TEXTO_SECUNDARIO = "#6b7280"


def analizar_seguridad_publica(df):
    if df is None or df.empty:
        return dbc.Alert(
            "⚠️ El archivo de Seguridad Pública no contiene registros válidos.",
            color="warning",
            className="m-3",
        )

    try:
        df_seg = df.copy()

        # Limpieza de nombres de columnas
        df_seg.columns = [str(c).strip() for c in df_seg.columns]
        columnas_reales = df_seg.columns.tolist()

        # Limpieza previa general de tipos mixtos en el DataFrame para evitar errores de float/str
        for col in columnas_reales:
            if not pd.api.types.is_numeric_dtype(df_seg[col]):
                df_seg[col] = df_seg[col].fillna("").astype(str).str.strip()
            else:
                df_seg[col] = df_seg[col].fillna(0)

        col_comunidad = columnas_reales[0]
        for c in columnas_reales:
            if any(
                term in c.lower()
                for term in ["comunidad", "localidad", "comunidades"]
            ):
                col_comunidad = c
                break

        col_reportes = next(
            (c for c in columnas_reales if "REPORTES" in c.upper()),
            "Reportes ciudadanos atendidos",
        )
        col_faltas = next(
            (c for c in columnas_reales if "FALTAS" in c.upper()),
            "Faltas administrativas",
        )
        col_accidentes = next(
            (c for c in columnas_reales if "ACCIDENTES" in c.upper()),
            "Cantidad de accidentes de tránsito atendidos",
        )
        col_catastrofes = next(
            (
                c
                for c in columnas_reales
                if "CATASTROFES" in c.upper() or "CATASTROFE" in c.upper()
            ),
            columnas_reales[4] if len(columnas_reales) > 4 else "Catastrofes",
        )
        col_mp = next(
            (
                c
                for c in columnas_reales
                if "MINISTERIO PÚBLICO" in c.upper()
                or "MINISTERIO PUBLICO" in c.upper()
            ),
            columnas_reales[5] if len(columnas_reales) > 5 else columnas_reales[0],
        )
        col_fgr = next(
            (
                c
                for c in columnas_reales
                if "FISCALIA" in c.upper() or "FGR" in c.upper()
            ),
            columnas_reales[6] if len(columnas_reales) > 6 else columnas_reales[0],
        )
        col_ubicacion = next(
            (
                c
                for c in columnas_reales
                if "UBICACIÓN" in c.upper() or "UBICACION" in c.upper()
            ),
            "Ubicación",
        )
        col_ruta = next(
            (c for c in columnas_reales if "RUTA" in c.upper()), "Ruta Asignada"
        )

        for col in [
            col_reportes,
            col_faltas,
            col_accidentes,
            col_catastrofes,
            col_mp,
            col_fgr,
        ]:
            if col in df_seg.columns:
                df_seg[col] = pd.to_numeric(df_seg[col], errors="coerce").fillna(
                    0
                )
            else:
                df_seg[col] = 0

        df_seg["TOTAL_ACCIONES"] = (
            df_seg[col_reportes]
            + df_seg[col_faltas]
            + df_seg[col_accidentes]
            + df_seg[col_catastrofes]
            + df_seg[col_mp]
            + df_seg[col_fgr]
        )

        latitudes, longitudes, links_mapa, rutas_limpias, comunidades_limpias = (
            [],
            [],
            [],
            [],
            [],
        )
        coordenadas_vistas = {}

        for _, row in df_seg.iterrows():
            val_comunidad = str(row.get(col_comunidad, "SIN NOMBRE")).strip()
            if (
                not val_comunidad
                or val_comunidad.upper() == "NAN"
                or len(val_comunidad) > 30
                or "FISCALIA" in val_comunidad.upper()
                or "PUESTAS" in val_comunidad.upper()
                or "MINISTERIO" in val_comunidad.upper()
            ):
                val_comunidad = "LOCALIDAD SIN NOMBRE"
            comunidades_limpias.append(val_comunidad)

            val_ubicacion = str(row.get(col_ubicacion, "")).strip()
            lat, lon = 21.155597, -98.903757
            if val_ubicacion and "," in val_ubicacion:
                try:
                    partes = val_ubicacion.split(",")
                    lat = float(partes[0].strip())
                    lon = float(partes[1].strip())
                except Exception:
                    pass

            coord_key = (round(lat, 5), round(lon, 5))
            if coord_key in coordenadas_vistas:
                lat += 0.0006 * coordenadas_vistas[coord_key]
                lon += 0.0006 * coordenadas_vistas[coord_key]
                coordenadas_vistas[coord_key] += 1
            else:
                coordenadas_vistas[coord_key] = 1

            latitudes.append(lat)
            longitudes.append(lon)
            links_mapa.append(
                "📍 Ver en Mapa"
                if (val_ubicacion and "," in val_ubicacion)
                else "Sin georreferencia"
            )

            val_ruta = (
                str(row.get(col_ruta, "SIN RUTA")).strip()
                if col_ruta
                else "SIN RUTA"
            )
            rutas_limpias.append(
                val_ruta
                if val_ruta and val_ruta.lower() != "nan"
                else "SIN RUTA"
            )

        df_seg["LAT_MAP"] = latitudes
        df_seg["LON_MAP"] = longitudes
        df_seg["UBICACION_MAPA_BTN"] = links_mapa
        df_seg["__COMUNIDAD_LIMPIA"] = comunidades_limpias
        df_seg["__RUTA_LIMPIA"] = rutas_limpias

        # ANÁLISIS DE RUTA MÁS CRÍTICA
        resumen_rutas = (
            df_seg.groupby("__RUTA_LIMPIA")["TOTAL_ACCIONES"]
            .sum()
            .reset_index()
        )
        if not resumen_rutas.empty:
            ruta_critica_row = resumen_rutas.loc[
                resumen_rutas["TOTAL_ACCIONES"].idxmax()
            ]
            nombre_ruta_critica = ruta_critica_row["__RUTA_LIMPIA"]
            total_acciones_critica = ruta_critica_row["TOTAL_ACCIONES"]
        else:
            nombre_ruta_critica = "N/A"
            total_acciones_critica = 0

        total_comunidades_atendidas = len(df_seg[df_seg["TOTAL_ACCIONES"] > 0])
        total_accidentes = df_seg[col_accidentes].sum()
        total_puestas = df_seg[col_mp].sum() + df_seg[col_fgr].sum()

        columnas_tabla = [
            {"name": "Comunidad / Localidad", "id": "__COMUNIDAD_LIMPIA"},
            {"name": "Ruta Asignada", "id": "__RUTA_LIMPIA"},
            {"name": "Reportes Ciudadanos", "id": col_reportes},
            {"name": "Faltas Administrativas", "id": col_faltas},
            {"name": "Accidentes de Tránsito", "id": col_accidentes},
            {"name": "Catástrofes", "id": col_catastrofes},
            {"name": "Total Acciones", "id": "TOTAL_ACCIONES"},
            {"name": "Ubicación Mapas", "id": "UBICACION_MAPA_BTN"},
        ]

        estilo_kpi = {
            "borderRadius": "8px",
            "cursor": "pointer",
            "transition": "all 0.25s ease-in-out",
            "backgroundColor": "white",
            "border": "1px solid #e5e7eb",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
        }

        tarjetas_kpi = dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "0",
                                    "left": "0",
                                    "bottom": "0",
                                    "width": "5px",
                                    "backgroundColor": VERDE_PRINCIPAL,
                                    "borderRadius": "8px 0 0 8px",
                                }
                            ),
                            html.Small(
                                "COMUNIDADES ATENDIDAS 🖱️",
                                className="font-weight-bold d-block",
                                style={
                                    "fontSize": "0.68rem",
                                    "letterSpacing": "0.5px",
                                    "color": TEXTO_SECUNDARIO,
                                },
                            ),
                            html.H3(
                                f"{total_comunidades_atendidas} Localidades",
                                className="m-0 font-weight-bold mt-1",
                                style={
                                    "color": TEXTO_DARK,
                                    "fontSize": "1.25rem",
                                },
                            ),
                            html.Small(
                                "Ver listado general",
                                className="d-block font-weight-bold",
                                style={
                                    "fontSize": "0.58rem",
                                    "marginTop": "3px",
                                    "color": VERDE_PRINCIPAL,
                                },
                            ),
                        ],
                        id="kpi-seguridad-click",
                        className="p-3 position-relative h-100",
                        style=estilo_kpi,
                    ),
                    width=12,
                    sm=6,
                    md=3,
                    className="mb-3",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "0",
                                    "left": "0",
                                    "bottom": "0",
                                    "width": "5px",
                                    "backgroundColor": GUINDA_INST,
                                    "borderRadius": "8px 0 0 8px",
                                }
                            ),
                            html.Small(
                                "RUTA MÁS CRÍTICA",
                                className="font-weight-bold d-block",
                                style={
                                    "fontSize": "0.68rem",
                                    "letterSpacing": "0.5px",
                                    "color": TEXTO_SECUNDARIO,
                                },
                            ),
                            html.H3(
                                f"{nombre_ruta_critica}",
                                className="m-0 font-weight-bold mt-1",
                                style={
                                    "color": GUINDA_INST,
                                    "fontSize": "1.25rem",
                                },
                            ),
                            html.Small(
                                f"Total: {total_acciones_critica:,.0f} acciones",
                                className="d-block font-weight-bold",
                                style={
                                    "fontSize": "0.58rem",
                                    "marginTop": "3px",
                                    "color": TEXTO_SECUNDARIO,
                                },
                            ),
                        ],
                        className="p-3 position-relative h-100",
                        style=estilo_kpi,
                    ),
                    width=12,
                    sm=6,
                    md=3,
                    className="mb-3",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "0",
                                    "left": "0",
                                    "bottom": "0",
                                    "width": "5px",
                                    "backgroundColor": VERDE_PRINCIPAL,
                                    "borderRadius": "8px 0 0 8px",
                                }
                            ),
                            html.Small(
                                "ACCIDENTES DE TRÁNSITO",
                                className="font-weight-bold d-block",
                                style={
                                    "fontSize": "0.68rem",
                                    "letterSpacing": "0.5px",
                                    "color": TEXTO_SECUNDARIO,
                                },
                            ),
                            html.H3(
                                f"{total_accidentes:,.0f}",
                                className="m-0 font-weight-bold mt-1",
                                style={
                                    "color": TEXTO_DARK,
                                    "fontSize": "1.25rem",
                                },
                            ),
                        ],
                        className="p-3 position-relative h-100",
                        style=estilo_kpi,
                    ),
                    width=12,
                    sm=6,
                    md=3,
                    className="mb-3",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "0",
                                    "left": "0",
                                    "bottom": "0",
                                    "width": "5px",
                                    "backgroundColor": GUINDA_INST,
                                    "borderRadius": "8px 0 0 8px",
                                }
                            ),
                            html.Small(
                                "PUESTAS A DISPOSICIÓN (MP / FGR)",
                                className="font-weight-bold d-block",
                                style={
                                    "fontSize": "0.68rem",
                                    "letterSpacing": "0.5px",
                                    "color": TEXTO_SECUNDARIO,
                                },
                            ),
                            html.H3(
                                f"{total_puestas:,.0f}",
                                className="m-0 font-weight-bold mt-1",
                                style={
                                    "color": VERDE_PRINCIPAL,
                                    "fontSize": "1.25rem",
                                },
                            ),
                        ],
                        className="p-3 position-relative h-100",
                        style=estilo_kpi,
                    ),
                    width=12,
                    sm=6,
                    md=3,
                    className="mb-3",
                ),
            ],
            className="mb-2",
        )

        desplegable_tabla = dbc.Collapse(
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-table me-2"),
                            (
                                "REGISTROS INTERNOS: INCIDENCIA Y ATENCIÓN POR"
                                " COMUNIDAD Y RUTA"
                            ),
                        ],
                        style={
                            "backgroundColor": VERDE_PRINCIPAL,
                            "color": "white",
                            "padding": "8px 12px",
                            "fontWeight": "bold",
                            "fontSize": "0.75rem",
                            "borderRadius": "6px 6px 0 0",
                        },
                    ),
                    html.Div(
                        [
                            dash_table.DataTable(
                                id="tabla-seguridad-comunidades",
                                data=df_seg.to_dict("records"),
                                columns=columnas_tabla,
                                page_size=6,
                                style_table={"overflowX": "auto"},
                                style_header={
                                    "backgroundColor": "#f3f4f6",
                                    "color": TEXTO_DARK,
                                    "fontWeight": "bold",
                                    "fontSize": "11px",
                                    "textAlign": "left",
                                    "borderBottom": "2px solid #e5e7eb",
                                },
                                style_cell={
                                    "padding": "10px 8px",
                                    "fontSize": "11px",
                                    "fontFamily": "sans-serif",
                                    "textAlign": "left",
                                    "borderBottom": "1px solid #f9fafb",
                                    "color": TEXTO_DARK,
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"row_index": "odd"},
                                        "backgroundColor": "#f9fafb",
                                    },
                                    {
                                        "if": {
                                            "column_id": "UBICACION_MAPA_BTN"
                                        },
                                        "color": VERDE_PRINCIPAL,
                                        "fontWeight": "bold",
                                        "cursor": "pointer",
                                    },
                                ],
                            )
                        ],
                        className="border border-top-0 p-2 bg-white",
                        style={"borderRadius": "0 0 6px 6px"},
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
            id="collapse-tabla-seguridad",
            is_open=False,
        )

        puntos_google_maps = []
        for _, row in df_seg.iterrows():
            puntos_google_maps.append(
                {
                    "lat": row["LAT_MAP"],
                    "lng": row["LON_MAP"],
                    "comunidad": row["__COMUNIDAD_LIMPIA"],
                    "ruta": row["__RUTA_LIMPIA"],
                    "reportes": str(row.get(col_reportes, 0)),
                    "faltas": str(row.get(col_faltas, 0)),
                    "accidentes": str(row.get(col_accidentes, 0)),
                    "catastrofes": str(row.get(col_catastrofes, 0)),
                    "total": str(row.get("TOTAL_ACCIONES", 0)),
                }
            )

        return html.Div(
            [
                dcc.Store(
                    id="store-mapa-seguridad-seleccion",
                    data={
                        "lat": 21.125,
                        "lng": -98.885,
                        "zoom": 12.5,
                        "comunidad": "",
                        "puntos": puntos_google_maps,
                    },
                ),
                tarjetas_kpi,
                desplegable_tabla,
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="bi bi-map-fill me-2",
                                                style={"color": DORADO_INST},
                                            ),
                                            (
                                                "VISOR GEOGRÁFICO INTERACTIVO DE"
                                                " SEGURIDAD PÚBLICA Y ATENCIÓN"
                                                " MUNICIPAL"
                                            ),
                                        ],
                                        style={
                                            "backgroundColor": VERDE_PRINCIPAL,
                                            "color": "white",
                                            "padding": "12px 16px",
                                            "fontWeight": "700",
                                            "fontSize": "0.75rem",
                                            "borderRadius": "6px 6px 0 0",
                                        },
                                    ),
                                    html.Iframe(
                                        id="iframe-mapa-seguridad",
                                        srcDoc="",
                                        width="100%",
                                        height="520",
                                        style={
                                            "border": "0",
                                            "borderRadius": "0 0 6px 6px",
                                        },
                                    ),
                                ],
                                className="bg-white border shadow-sm mb-3",
                                style={"borderRadius": "6px"},
                            ),
                            md=12,
                        )
                    ]
                ),
            ],
            style={"padding": "5px"},
        )

    except Exception as e:
        return dbc.Alert(
            f"⚠️ Error al construir estadísticas: {str(e)}",
            color="danger",
            className="m-3",
        )


@callback(
    Output("collapse-tabla-seguridad", "is_open"),
    Input("kpi-seguridad-click", "n_clicks"),
    State("collapse-tabla-seguridad", "is_open"),
    prevent_initial_call=True,
)
def alternar_desplegable_seguridad(n_clicks, estado_actual):
    if n_clicks:
        return not estado_actual
    return estado_actual


@callback(
    Output("store-mapa-seguridad-seleccion", "data"),
    Input("tabla-seguridad-comunidades", "active_cell"),
    State("tabla-seguridad-comunidades", "data"),
    State("store-mapa-seguridad-seleccion", "data"),
    prevent_initial_call=True,
)
def capturar_clic_ubicacion_seguridad(active_cell, dataset, current_store):
    if not active_cell or not dataset:
        return dash.no_update

    if active_cell.get("column_id") == "UBICACION_MAPA_BTN":
        row_idx = active_cell.get("row")
        if row_idx is not None and 0 <= row_idx < len(dataset):
            row_data = dataset[row_idx]
            puntos_actuales = (
                current_store.get("puntos", []) if current_store else []
            )
            comunidad_val = str(
                row_data.get("__COMUNIDAD_LIMPIA", "")
            ).strip()
            return {
                "lat": float(row_data.get("LAT_MAP", 21.125)),
                "lng": float(row_data.get("LON_MAP", -98.885)),
                "zoom": 16,
                "comunidad": comunidad_val,
                "puntos": puntos_actuales,
            }

    return dash.no_update


@callback(
    Output("iframe-mapa-seguridad", "srcDoc"),
    Input("store-mapa-seguridad-seleccion", "data"),
)
def actualizar_mapa_seguridad_html(sel_data):
    if not sel_data:
        return ""

    target_lat = sel_data.get("lat", 21.125)
    target_lng = sel_data.get("lng", -98.885)
    target_zoom = sel_data.get("zoom", 12.5)
    target_comunidad = sel_data.get("comunidad", "")
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
            max-width: 220px;
        }}
        .legend h4 {{
            margin: 0 0 6px 0;
            font-size: 12px;
            font-weight: bold;
            color: #0f4c3a;
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
        .community-badge {{
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #bc955c;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            font-weight: bold;
            color: #0f4c3a;
            white-space: nowrap;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
    <div id="map" style="width: 100%; height: 100%;"></div>
    <script>
        var bounds = [
            [20.95, -99.20],
            [21.38, -98.60]
        ];

        var map = L.map('map', {{
            minZoom: 12,
            maxZoom: 18,
            maxBounds: bounds,
            maxBoundsViscosity: 1.0
        }}).setView([{target_lat}, {target_lng}], {target_zoom});
        
        L.tileLayer('https://{{s}}.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            subdomains:['mt0','mt1','mt2','mt3'],
            attribution: '&copy; Google Maps'
        }}).addTo(map);

        function getColor(totalAcciones) {{
            var t = parseInt(totalAcciones) || 0;
            if (t > 20) return "#0f4c3a";
            if (t > 10) return "#691c32";
            if (t > 5) return "#bc955c";
            if (t > 0) return "#2563eb";
            return "#9ca3af";
        }}

        function getRadius(totalAcciones) {{
            var t = parseInt(totalAcciones) || 0;
            if (t > 20) return 13;
            if (t > 10) return 10;
            if (t > 5) return 8;
            if (t > 0) return 6;
            return 5;
        }}

        var legend = L.control({{position: 'topright'}});
        legend.onAdd = function (map) {{
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<h4>Nivel de Incidencia</h4>' +
                '<div class="legend-item"><i style="background:#0f4c3a"></i>Alta (> 20 eventos)</div>' +
                '<div class="legend-item"><i style="background:#691c32"></i>Media-Alta (11 - 20)</div>' +
                '<div class="legend-item"><i style="background:#bc955c"></i>Media (6 - 10)</div>' +
                '<div class="legend-item"><i style="background:#2563eb"></i>Baja (1 - 5)</div>' +
                '<div class="legend-item"><i style="background:#9ca3af"></i>Sin registros</div>';
            return div;
        }};
        legend.addTo(map);

        var puntos = {puntos_json};
        var markersGroup = L.layerGroup().addTo(map);
        var targetMarker = null;

        puntos.forEach(function(p) {{
            if (p.lat && p.lng) {{
                var colorMark = getColor(p.total);
                var radiusSize = getRadius(p.total);

                var marker = L.circleMarker([p.lat, p.lng], {{
                    radius: radiusSize,
                    fillColor: colorMark,
                    color: "#ffffff",
                    weight: 2.5,
                    opacity: 1,
                    fillOpacity: 0.92
                }});

                var popupContent = '<div class="custom-popup">' +
                    '<b>Comunidad:</b> ' + p.comunidad + '<br>' +
                    '<b>Ruta Asignada:</b> ' + p.ruta + '<br>' +
                    '<b>Reportes Ciudadanos:</b> ' + p.reportes + '<br>' +
                    '<b>Faltas Administrativas:</b> ' + p.faltas + '<br>' +
                    '<b>Accidentes Tránsito:</b> ' + p.accidentes + '<br>' +
                    '<b>Catástrofes:</b> ' + p.catastrofes + '<br>' +
                    '<b>Total Acciones:</b> ' + p.total +
                    '</div>';

                marker.bindPopup(popupContent);
                marker.addTo(markersGroup);

                map.on('zoomend', function() {{
                    if (map.getZoom() >= 14) {{
                        if (!marker.badgeTooltip) {{
                            marker.badgeTooltip = L.marker([p.lat, p.lng], {{
                                icon: L.divIcon({{
                                    className: 'community-badge',
                                    html: p.comunidad,
                                    iconSize: [null, 18],
                                    iconAnchor: [-12, 10]
                                }})
                            }}).addTo(map);
                        }}
                    }} else {{
                        if (marker.badgeTooltip) {{
                            map.removeLayer(marker.badgeTooltip);
                            marker.badgeTooltip = null;
                        }}
                    }}
                }});

                if ("{target_comunidad}" !== "" && p.comunidad === "{target_comunidad}" && Math.abs(p.lat - {target_lat}) < 0.0001) {{
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