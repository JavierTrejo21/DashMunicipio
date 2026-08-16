# areas/atencion_ciudadana.py
import dash
import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    State,
    callback,
    callback_context,
    dash_table,
    dcc,
    html,
)
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# PALETA INSTITUCIONAL DEL SISTEMA
# ==========================================================
GUINDA = "#781D37"
GUINDA_DARK = "#54132A"
GUINDA_LIGHT = "#F3E7EB"
VERDE = "#1CA2A9"
VERDE_DARK = "#147880"
VERDE_LIGHT = "#E3F5F6"
BG = "#EFEDE6"
CARD = "#FFFFFF"
INK = "#241E1B"
INK_SOFT = "#6B625C"
INK_FAINT = "#9B928C"
LINE = "#E3DDD2"

FONT_SANS = "'Inter', sans-serif"
FONT_SERIF = "'Playfair Display', serif"

ORDEN_MESES = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]


def _fuentes_e_iconos():
  return html.Div([
      html.Link(rel="preconnect", href="https://fonts.googleapis.com"),
      html.Link(
          rel="stylesheet",
          href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap",
      ),
      html.Link(
          rel="stylesheet",
          href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css",
      ),
  ])


def _section_label(icono, texto):
  return html.Div(
      [
          html.I(
              className=f"ti {icono}",
              style={"color": VERDE, "fontSize": "16px"},
          ),
          html.Span(
              texto,
              style={
                  "fontFamily": FONT_SERIF,
                  "fontWeight": "700",
                  "fontSize": "14px",
                  "letterSpacing": ".04em",
                  "color": GUINDA_DARK,
                  "textTransform": "uppercase",
                  "whiteSpace": "nowrap",
              },
          ),
          html.Div(style={"flex": "1", "height": "1px", "background": LINE}),
      ],
      style={
          "display": "flex",
          "alignItems": "center",
          "gap": "9px",
          "margin": "22px 0 16px",
      },
  )


def _kpi_card(icono, eyebrow, valor, sub, color=VERDE):
  color_light = VERDE_LIGHT if color == VERDE else GUINDA_LIGHT
  color_dark = VERDE_DARK if color == VERDE else GUINDA_DARK
  return html.Div(
      [
          html.Div(
              [
                  html.Div(
                      html.Div(
                          html.I(className=f"ti {icono}"),
                          style={
                              "width": "100%",
                              "height": "100%",
                              "borderRadius": "50%",
                              "background": color_light,
                              "display": "flex",
                              "alignItems": "center",
                              "justifyContent": "center",
                              "fontSize": "20px",
                              "color": color_dark,
                              "border": "1px solid #fff",
                          },
                      ),
                      style={
                          "width": "50px",
                          "height": "50px",
                          "borderRadius": "50%",
                          "flexShrink": "0",
                          "padding": "3px",
                          "background": (
                              f"conic-gradient({color} 100%, {LINE} 0)"
                          ),
                      },
                  ),
                  html.Div(
                      [
                          html.Div(
                              eyebrow,
                              style={
                                  "fontSize": "9.5px",
                                  "fontWeight": "700",
                                  "letterSpacing": ".08em",
                                  "color": INK_FAINT,
                                  "textTransform": "uppercase",
                                  "marginBottom": "3px",
                              },
                          ),
                          html.Div(
                              valor,
                              style={
                                  "fontWeight": "700",
                                  "fontSize": "17px",
                                  "lineHeight": "1.25",
                                  "color": INK,
                              },
                          ),
                          html.Div(
                              sub,
                              style={
                                  "fontSize": "10.5px",
                                  "color": INK_SOFT,
                                  "marginTop": "3px",
                              },
                          )
                          if sub
                          else None,
                      ],
                      style={"flex": "1", "minWidth": "0"},
                  ),
              ],
              style={
                  "display": "flex",
                  "alignItems": "center",
                  "gap": "14px",
              },
          ),
      ],
      style={
          "background": CARD,
          "border": f"1px solid {LINE}",
          "borderRadius": "8px",
          "position": "relative",
          "padding": "18px 20px",
          "boxShadow": "0 1px 2px rgba(84,19,42,.05)",
          "borderTop": f"3px solid {color}",
          "height": "100%",
          "boxSizing": "border-box",
      },
  )


def analizar_atencion_ciudadana(df):
  if df is None or df.empty:
    return dbc.Alert(
        "⚠️ El archivo de Atención Ciudadana no contiene registros válidos o"
        " está vacío.",
        color="warning",
    )

  # --- HOMOLOGACIÓN DE COLUMNAS EN MAYÚSCULAS ---
  df_atc = df.copy()
  df_atc.columns = [str(c).strip().upper() for c in df_atc.columns]
  columnas_reales = df_atc.columns.tolist()

  col_mes = next((c for c in columnas_reales if "MES" in c), "MES")
  col_atn = next(
      (c for c in columnas_reales if "ATEN" in c or "ATEND" in c), "ATENDIDOS"
  )
  col_act = next((c for c in columnas_reales if "ACT" in c), "ACTIVIDAD")
  col_var = next((c for c in columnas_reales if "VAR" in c or "AREA" in c), "VARIABLE")

  # --- LIMPIEZA RIGUROSA ---
  df_atc[col_atn] = (
      pd.to_numeric(df_atc[col_atn], errors="coerce").fillna(0).astype(int)
  )
  df_atc[col_var] = (
      df_atc[col_var].fillna("OTRAS ÁREAS").astype(str).str.strip().str.upper()
  )
  df_atc[col_act] = (
      df_atc[col_act].fillna("SIN ESPECIFICAR").astype(str).str.strip()
  )
  df_atc[col_mes] = (
      df_atc[col_mes].fillna("S/M").astype(str).str.strip().str.upper()
  )

  total_atendidos = int(df_atc[col_atn].sum())
  df_areas = df_atc.groupby(col_var)[col_atn].sum().reset_index()
  df_areas = df_areas.sort_values(by=col_atn, ascending=False)
  area_mas_solicitada = (
      df_areas.iloc[0][col_var] if not df_areas.empty else "N/D"
  )

  # --- TOP 3 ACTIVIDADES ---
  df_actividades_top = (
      df_atc.groupby(col_act)[col_atn].sum().reset_index()
  )
  df_actividades_top = df_actividades_top.sort_values(
      by=col_atn, ascending=False
  ).head(3)

  lista_top_actividades = []
  for i, (_, row) in enumerate(df_actividades_top.iterrows(), start=1):
    nombre_act = row[col_act]
    total_act = row[col_atn]
    lista_top_actividades.append(
        html.Div(
            [
                html.Span(
                    f"{i}. {nombre_act}",
                    style={
                        "fontWeight": "600",
                        "color": INK,
                        "fontSize": "11.5px",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "flex": "1",
                    },
                ),
                html.Span(
                    f"{total_act:,} Ciudadanos",
                    style={
                        "fontWeight": "700",
                        "color": VERDE_DARK,
                        "fontSize": "11px",
                        "marginLeft": "8px",
                    },
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "4px",
            },
        )
    )

  if not lista_top_actividades:
    lista_top_actividades = [
        html.Span(
            "Sin registros", style={"fontSize": "11px", "color": INK_SOFT}
        )
    ]

  df_areas["VALOR_COLOR"] = np.log1p(df_areas[col_atn])

  kpis_row = dbc.Row([
      dbc.Col(
          _kpi_card(
              "ti-users",
              "Total de ciudadanos atendidos",
              f"{total_atendidos:,}",
              "Registros del periodo",
              VERDE,
          ),
          width=12,
          md=4,
          className="mb-3",
      ),
      dbc.Col(
          _kpi_card(
              "ti-star",
              "Área de mayor afluencia",
              area_mas_solicitada,
              "Departamento con más solicitudes",
              GUINDA,
          ),
          width=12,
          md=4,
          className="mb-3",
      ),
      dbc.Col(
          html.Div(
              [
                  html.Div(
                      [
                          html.Div(
                              html.Div(
                                  html.I(className="ti-list-details"),
                                  style={
                                      "width": "100%",
                                      "height": "100%",
                                      "borderRadius": "50%",
                                      "background": VERDE_LIGHT,
                                      "display": "flex",
                                      "alignItems": "center",
                                      "justifyContent": "center",
                                      "fontSize": "20px",
                                      "color": VERDE_DARK,
                                      "border": "1px solid #fff",
                                  },
                              ),
                              style={
                                  "width": "50px",
                                  "height": "50px",
                                  "borderRadius": "50%",
                                  "flexShrink": "0",
                                  "padding": "3px",
                                  "background": (
                                      f"conic-gradient({VERDE} 100%, {LINE} 0)"
                                  ),
                              },
                          ),
                          html.Div(
                              [
                                  html.Div(
                                      "Top 3 Actividades Frecuentes",
                                      style={
                                          "fontSize": "9.5px",
                                          "fontWeight": "700",
                                          "letterSpacing": ".08em",
                                          "color": INK_FAINT,
                                          "textTransform": "uppercase",
                                          "marginBottom": "4px",
                                      },
                                  ),
                                  html.Div(
                                      lista_top_actividades,
                                      style={
                                          "display": "flex",
                                          "flexDirection": "column",
                                      },
                                  ),
                              ],
                              style={"flex": "1", "minWidth": "0"},
                          ),
                      ],
                      style={
                          "display": "flex",
                          "alignItems": "flex-start",
                          "gap": "14px",
                      },
                  ),
              ],
              style={
                  "background": CARD,
                  "border": f"1px solid {LINE}",
                  "borderRadius": "8px",
                  "position": "relative",
                  "padding": "15px 20px",
                  "boxShadow": "0 1px 2px rgba(84,19,42,.05)",
                  "borderTop": f"3px solid {VERDE}",
                  "height": "100%",
                  "boxSizing": "border-box",
              },
          ),
          width=12,
          md=4,
          className="mb-3",
      ),
  ])

  estilos_animacion = dcc.Markdown(
      """
<style>
    @keyframes fadeInSlide {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .animar-entrada {
        animation: fadeInSlide 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .tarjeta-flotante-moderna {
        animation: fadeInSlide 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
</style>
""",
      dangerously_allow_html=True,
  )

  fig_treemap = px.treemap(
      df_areas,
      path=[col_var],
      values=col_atn,
      color="VALOR_COLOR",
      color_continuous_scale=[
          [0.0, "#0E4C52"],
          [0.25, "#147880"],
          [0.5, VERDE],
          [0.75, "#54132A"],
          [1.0, GUINDA],
      ],
      custom_data=[col_atn],
  )

  fig_treemap.update_traces(
      texttemplate="<b>%{label}</b><br>%{value:,} Ciudadanos",
      textposition="middle center",
      insidetextfont=dict(size=13, family="Inter, sans-serif", color="#FFFFFF"),
      outsidetextfont=dict(size=11, family="Inter, sans-serif", color=INK),
      marker=dict(cornerradius=4),
      hovertemplate=(
          "<b>Área:</b> %{label}<br><b>Ciudadanos Atendidos:"
          "</b> %{value:,}<extra></extra>"
      ),
  )

  fig_treemap.update_layout(
      margin=dict(l=10, r=10, t=10, b=10),
      coloraxis_showscale=False,
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      height=420,
      font=dict(family="Inter, sans-serif"),
  )

  store_data = dcc.Store(
      id="store-atencion-data", data=df_atc.to_dict("records")
  )
  store_seleccion = dcc.Store(id="store-area-seleccionada", data=None)

  seccion_treemap = html.Div(
      html.Div(
          [
              html.Div(
                  "Concentración y distribución de presencia ciudadana por"
                  " departamento",
                  style={
                      "fontSize": "11px",
                      "fontWeight": "700",
                      "letterSpacing": ".03em",
                      "textTransform": "uppercase",
                      "color": INK_SOFT,
                      "marginBottom": "10px",
                  },
              ),
              html.Div([
                  html.P(
                      "Haz clic en cualquier departamento para consultar su"
                      " detalle en la tarjeta flotante.",
                      style={
                          "fontSize": "12px",
                          "color": INK_SOFT,
                          "textAlign": "center",
                          "marginBottom": "8px",
                      },
                  ),
                  html.Div(
                      [
                          dcc.Graph(
                              id="treemap-atencion",
                              figure=fig_treemap,
                              config={"displayModeBar": False},
                          ),
                          html.Div(
                              [
                                  html.Div(
                                      [
                                          html.Div(
                                              [
                                                  html.I(
                                                      className="ti-info-circle",
                                                      style={
                                                          "color": VERDE,
                                                          "fontSize": "13px",
                                                      },
                                                  ),
                                                  html.Span(
                                                      "Detalle de Área",
                                                      style={
                                                          "fontSize": "10px",
                                                          "fontWeight": "700",
                                                          "letterSpacing": (
                                                              ".06em"
                                                          ),
                                                          "textTransform": (
                                                              "uppercase"
                                                          ),
                                                          "color": INK_SOFT,
                                                      },
                                                  ),
                                              ],
                                              style={
                                                  "display": "flex",
                                                  "alignItems": "center",
                                                  "gap": "6px",
                                              },
                                          ),
                                      ],
                                      style={
                                          "display": "flex",
                                          "justifyContent": "space-between",
                                          "alignItems": "center",
                                          "marginBottom": "8px",
                                          "paddingBottom": "4px",
                                          "borderBottom": f"1px solid {LINE}",
                                      },
                                  ),
                                  html.Div(id="contenido-detalle-area"),
                              ],
                              id="detalle-area-seleccionada",
                              className="tarjeta-flotante-moderna",
                              style={
                                  "position": "absolute",
                                  "top": "8%",
                                  "left": "4%",
                                  "width": "30%",
                                  "maxHeight": "82%",
                                  "zIndex": "20",
                                  "overflowY": "auto",
                                  "background": "rgba(255, 255, 255, 0.96)",
                                  "backdropFilter": "blur(4px)",
                                  "border": f"1px solid {LINE}",
                                  "borderRadius": "8px",
                                  "borderLeft": f"3px solid {VERDE}",
                                  "padding": "12px 14px",
                                  "boxShadow": (
                                      "0 8px 24px rgba(36, 30, 27, 0.12)"
                                  ),
                                  "display": "none",
                              },
                          ),
                      ],
                      style={"position": "relative", "width": "100%"},
                  ),
              ]),
          ],
          style={
              "background": CARD,
              "border": f"1px solid {LINE}",
              "borderRadius": "8px",
              "borderTop": f"3px solid {GUINDA}",
              "padding": "16px 18px 12px",
              "overflow": "hidden",
          },
      ),
      className="animar-entrada mb-3",
  )

  # Gráfica de línea temporal
  fig_linea = go.Figure()
  df_meses = df_atc.groupby(col_mes)[col_atn].sum().reset_index()
  df_meses["orden"] = df_meses[col_mes].apply(
      lambda x: ORDEN_MESES.index(x) if x in ORDEN_MESES else 99
  )
  df_meses = df_meses.sort_values("orden")

  if not df_meses.empty:
    fig_linea.add_trace(
        go.Scatter(
            x=df_meses[col_mes],
            y=df_meses[col_atn],
            mode="lines+markers+text",
            line=dict(color=GUINDA, width=3, shape="spline"),
            marker=dict(color=VERDE, size=9, line=dict(width=2, color="white")),
            text=df_meses[col_atn].apply(lambda x: f"<b>{int(x):,}</b>"),
            textposition="top center",
            textfont=dict(size=10, color=INK_SOFT, family="Inter, sans-serif"),
            fill="tozeroy",
            fillcolor=f"rgba(120, 29, 55, 0.06)",
            hovertemplate=(
                "<b>Mes:</b> %{x}<br><b>Atendidos:</b> %{y:,}"
                " ciudadanos<extra></extra>"
            ),
        )
    )

  fig_linea.update_layout(
      margin=dict(l=20, r=20, t=10, b=20),
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      height=260,
      xaxis=dict(
          showgrid=False,
          tickfont=dict(color=INK_SOFT, size=10, family="Inter, sans-serif"),
      ),
      yaxis=dict(showgrid=True, gridcolor=LINE, showticklabels=False),
      font=dict(family="Inter, sans-serif"),
  )

  seccion_linea = html.Div(
      html.Div(
          [
              html.Div(
                  "Comportamiento histórico y fluctuación mensual de"
                  " audiencias",
                  style={
                      "fontSize": "11px",
                      "fontWeight": "700",
                      "letterSpacing": ".03em",
                      "textTransform": "uppercase",
                      "color": INK_SOFT,
                      "marginBottom": "10px",
                  },
              ),
              html.Div([
                  html.P(
                      "Monitoreo temporal para identificar picos estacionales"
                      " de solicitudes en el municipio.",
                      style={
                          "fontSize": "12px",
                          "color": INK_SOFT,
                          "textAlign": "center",
                          "marginBottom": "8px",
                      },
                  ),
                  dcc.Graph(
                      figure=fig_linea, config={"displayModeBar": False}
                  ),
              ]),
          ],
          style={
              "background": CARD,
              "border": f"1px solid {LINE}",
              "borderRadius": "8px",
              "borderTop": f"3px solid {VERDE}",
              "padding": "16px 18px 12px",
              "overflow": "hidden",
          },
      ),
      className="animar-entrada mb-3",
  )

  # --- SECCIÓN TABLA DETALLADA CON FILTRO / SELECTOR DE ÁREA ---
  areas_disponibles = sorted(df_atc[col_var].unique().tolist())
  opciones_dropdown = [{"label": "Todas las áreas", "value": "TODAS"}] + [
      {"label": a, "value": a} for a in areas_disponibles
  ]

  columnas_tabla = [
      {"name": "Mes", "id": col_mes},
      {"name": "Área / Dirección", "id": col_var},
      {"name": "Actividad", "id": col_act},
      {"name": "Ciudadanos Atendidos", "id": col_atn},
  ]

  seccion_tabla = html.Div(
      html.Div(
          [
              html.Div(
                  [
                      html.Div(
                          "Registro detallado de atención ciudadana",
                          style={
                              "fontSize": "11px",
                              "fontWeight": "700",
                              "letterSpacing": ".03em",
                              "textTransform": "uppercase",
                              "color": INK_SOFT,
                          },
                      ),
                      html.Div(
                          [
                              html.Span(
                                  "Filtrar área:",
                                  style={
                                      "fontSize": "11px",
                                      "fontWeight": "600",
                                      "color": INK_SOFT,
                                  },
                              ),
                              dcc.Dropdown(
                                  id="dropdown-filtro-tabla-atc",
                                  options=opciones_dropdown,
                                  value="TODAS",
                                  clearable=False,
                                  style={
                                      "width": "240px",
                                      "fontSize": "12px",
                                      "fontFamily": "Inter, sans-serif",
                                  },
                              ),
                          ],
                          style={
                              "display": "flex",
                              "alignItems": "center",
                              "gap": "10px",
                          },
                      ),
                  ],
                  style={
                      "display": "flex",
                      "justifyContent": "space-between",
                      "alignItems": "center",
                      "marginBottom": "12px",
                      "flexWrap": "wrap",
                      "gap": "10px",
                  },
              ),
              html.Div(
                  id="contenedor-tabla-detalle-atc",
                  children=[
                      dash_table.DataTable(
                          id="tabla-detalle-atc",
                          data=df_atc.to_dict("records"),
                          columns=columnas_tabla,
                          page_size=8,
                          style_table={
                              "overflowX": "auto",
                              "overflowY": "auto",
                              "maxHeight": "320px",
                          },
                          style_header={
                              "backgroundColor": GUINDA_DARK,
                              "color": "#ffffff",
                              "fontWeight": "700",
                              "fontSize": "10.5px",
                              "letterSpacing": ".04em",
                              "textTransform": "uppercase",
                              "textAlign": "left",
                              "border": "none",
                              "fontFamily": "Inter, sans-serif",
                              "padding": "10px 14px",
                          },
                          style_cell={
                              "padding": "10px 14px",
                              "fontSize": "12px",
                              "fontFamily": "Inter, sans-serif",
                              "color": INK,
                              "textAlign": "left",
                              "borderBottom": f"1px solid {LINE}",
                              "backgroundColor": CARD,
                          },
                          style_data_conditional=[
                              {
                                  "if": {"row_index": "odd"},
                                  "backgroundColor": "#FAF8F4",
                              },
                          ],
                      )
                  ],
              ),
          ],
          style={
              "background": CARD,
              "border": f"1px solid {LINE}",
              "borderRadius": "8px",
              "borderTop": f"3px solid {GUINDA}",
              "padding": "16px 18px 12px",
              "overflow": "hidden",
          },
      ),
      className="animar-entrada mb-3",
  )

  return html.Div(
      [
          _fuentes_e_iconos(),
          estilos_animacion,
          store_data,
          store_seleccion,
          _section_label("ti-chart-bar", "Resumen general"),
          kpis_row,
          _section_label("ti-layout-grid", "Distribución por departamento"),
          seccion_treemap,
          _section_label("ti-chart-line", "Tendencia mensual"),
          seccion_linea,
          _section_label("ti-table", "Registro detallado"),
          seccion_tabla,
      ],
      style={
          "background": BG,
          "fontFamily": FONT_SANS,
          "color": INK,
          "padding": "5px",
      },
  )


# =================================================================
# CALLBACKS PARA GESTIONAR LA SELECCIÓN Y APERTURA/CIERRE AUTOMÁTICO
# =================================================================


@callback(
    [
        Output("store-area-seleccionada", "data"),
        Output("treemap-atencion", "clickData"),
    ],
    Input("treemap-atencion", "clickData"),
    State("store-area-seleccionada", "data"),
    prevent_initial_call=True,
)
def gestionar_seleccion_area(clickData, area_actual):
  if not clickData:
    return dash.no_update, dash.no_update

  try:
    nueva_area = clickData["points"][0]["label"]
    if nueva_area == area_actual:
      return None, None
    return nueva_area, dash.no_update
  except (KeyError, IndexError):
    pass

  return dash.no_update, dash.no_update


@callback(
    [
        Output("detalle-area-seleccionada", "style"),
        Output("contenido-detalle-area", "children"),
    ],
    Input("store-area-seleccionada", "data"),
    State("store-atencion-data", "data"),
)
def renderizar_tarjeta_flotante(area_seleccionada, stored_data):
  base_style = {
      "position": "absolute",
      "top": "8%",
      "left": "4%",
      "width": "30%",
      "maxHeight": "82%",
      "zIndex": "20",
      "overflowY": "auto",
      "background": "rgba(255, 255, 255, 0.96)",
      "backdropFilter": "blur(4px)",
      "border": f"1px solid {LINE}",
      "borderRadius": "8px",
      "borderLeft": f"3px solid {VERDE}",
      "padding": "12px 14px",
      "boxShadow": "0 8px 24px rgba(36, 30, 27, 0.12)",
  }

  if not area_seleccionada or not stored_data:
    base_style["display"] = "none"
    return base_style, html.Div()

  base_style["display"] = "block"

  df_sub = pd.DataFrame(stored_data)
  if df_sub.empty:
    return base_style, html.Div()

  col_var = next(
      (c for c in df_sub.columns if "VAR" in c or "AREA" in c), "VARIABLE"
  )
  col_atn = next(
      (c for c in df_sub.columns if "ATEN" in c or "ATEND" in c), "ATENDIDOS"
  )
  col_act = next((c for c in df_sub.columns if "ACT" in c), "ACTIVIDAD")
  col_mes = next((c for c in df_sub.columns if "MES" in c), "MES")

  df_sub = df_sub[df_sub[col_var] == area_seleccionada]
  if df_sub.empty:
    return base_style, html.Div()

  df_actividades = df_sub.groupby(col_act)[col_atn].sum().reset_index()
  df_actividades = df_actividades.sort_values(by=col_atn, ascending=False)

  df_mes_area = df_sub.groupby(col_mes)[col_atn].sum().reset_index()
  df_mes_area["orden"] = df_mes_area[col_mes].apply(
      lambda x: ORDEN_MESES.index(x) if x in ORDEN_MESES else 99
  )
  df_mes_area = df_mes_area.sort_values(
      by=[col_atn, "orden"], ascending=[False, True]
  )

  mes_mayor_flujo = (
      df_mes_area.iloc[0][col_mes] if not df_mes_area.empty else "N/D"
  )
  ciudadanos_mes_max = (
      df_mes_area.iloc[0][col_atn] if not df_mes_area.empty else 0
  )

  tabla_actividades = dash_table.DataTable(
      data=df_actividades.to_dict("records"),
      columns=[
          {"name": "Actividad", "id": col_act},
          {"name": "Atendidos", "id": col_atn},
      ],
      page_size=4,
      style_table={"overflowX": "auto", "maxHeight": "140px"},
      style_header={
          "backgroundColor": VERDE_DARK,
          "color": "#ffffff",
          "fontWeight": "700",
          "fontSize": "9.5px",
          "textTransform": "uppercase",
          "textAlign": "left",
          "border": "none",
          "padding": "5px 8px",
      },
      style_cell={
          "padding": "6px 8px",
          "fontSize": "10.5px",
          "fontFamily": "Inter, sans-serif",
          "color": INK,
          "textAlign": "left",
          "borderBottom": f"1px solid {LINE}",
          "backgroundColor": "rgba(255,255,255,0.7)",
      },
      style_data_conditional=[
          {"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"},
      ],
  )

  contenido_detalle = html.Div([
      html.Div(
          [
              html.Div(
                  area_seleccionada,
                  style={
                      "color": GUINDA_DARK,
                      "fontSize": "11.5px",
                      "fontWeight": "700",
                      "lineHeight": "1.3",
                  },
              ),
              html.Div(
                  f"Pico: {mes_mayor_flujo} ({ciudadanos_mes_max:,} civ.)",
                  style={
                      "fontSize": "10px",
                      "color": VERDE_DARK,
                      "marginTop": "2px",
                      "fontWeight": "600",
                  },
              ),
          ],
          style={
              "marginBottom": "8px",
              "padding": "6px 8px",
              "background": "#F7F5F0",
              "borderRadius": "4px",
              "borderLeft": f"2.5px solid {GUINDA}",
          },
      ),
      tabla_actividades,
  ])

  return base_style, contenido_detalle


# =================================================================
# CALLBACK PARA FILTRAR LA TABLA DETALLADA MEDIANTE EL DROPDOWN
# =================================================================


@callback(
    Output("tabla-detalle-atc", "data"),
    Input("dropdown-filtro-tabla-atc", "value"),
    State("store-atencion-data", "data"),
)
def filtrar_tabla_por_area(area_seleccionada, stored_data):
  if not stored_data:
    return []

  df = pd.DataFrame(stored_data)
  if df.empty:
    return []

  col_var = next(
      (c for c in df.columns if "VAR" in c or "AREA" in c), "VARIABLE"
  )

  if not area_seleccionada or area_seleccionada == "TODAS":
    return df.to_dict("records")

  df_filtrado = df[df[col_var] == area_seleccionada]
  return df_filtrado.to_dict("records")