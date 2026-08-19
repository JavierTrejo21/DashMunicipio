import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, dcc, html
import pandas as pd
import plotly.express as px

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


def _fuentes_e_iconos():
  return html.Div([
      html.Link(rel="preconnect", href="https://fonts.googleapis.com"),
      html.Link(
          rel="stylesheet",
          href=(
              "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap"
          ),
      ),
      html.Link(
          rel="stylesheet",
          href=(
              "https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css"
          ),
      ),
  ])


def _section_label(icono, texto):
  return html.Div(
      [
          html.I(
              className=f"ti {icono}", style={"color": VERDE, "fontSize": "16px"}
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
          html.Div(
              style={"flex": "1", "height": "1px", "background": LINE}
          ),
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
                          "background": f"conic-gradient({color} 100%, {LINE} 0)",
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
              style={"display": "flex", "alignItems": "center", "gap": "14px"},
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


def _chart_panel(titulo, contenido, color_top=GUINDA):
  return html.Div(
      [
          html.Div(
              titulo,
              style={
                  "fontSize": "11px",
                  "fontWeight": "700",
                  "letterSpacing": ".03em",
                  "textTransform": "uppercase",
                  "color": INK_SOFT,
                  "marginBottom": "10px",
              },
          ),
          contenido,
      ],
      style={
          "background": CARD,
          "border": f"1px solid {LINE}",
          "borderRadius": "8px",
          "borderTop": f"3px solid {color_top}",
          "padding": "16px 18px 8px",
          "overflow": "hidden",
      },
  )


ID_DROPDOWN_VAR_UBR = "ubr-variable-dropdown"
ID_TABLA_DETALLE_UBR = "ubr-tabla-detalle"
_cache_detalle_ubr = {"data": pd.DataFrame()}


def _tabla_detalle_ubr(df_detalle, columnas_mostrar, etiquetas):
  columnas = [{"name": etiquetas.get(c, c), "id": c} for c in columnas_mostrar]
  variables_opciones = (
      sorted(df_detalle["VARIABLE"].dropna().unique().tolist())
      if "VARIABLE" in df_detalle.columns
      else []
  )

  selector = html.Div(
      [
          html.Div(
              [
                  html.I(
                      className="ti ti-search",
                      style={
                          "color": VERDE,
                          "fontSize": "14px",
                          "marginRight": "6px",
                      },
                  ),
                  html.Span(
                      "CONSULTA DETALLADA POR ACTIVIDAD Y CLASIFICACIÓN UBR",
                      style={
                          "fontFamily": FONT_SERIF,
                          "fontWeight": "700",
                          "fontSize": "12.5px",
                          "letterSpacing": ".03em",
                          "color": GUINDA_DARK,
                          "textTransform": "uppercase",
                      },
                  ),
              ],
              style={
                  "display": "flex",
                  "alignItems": "center",
                  "marginBottom": "8px",
              },
          ),
          html.Div(
              "Filtra por categoría general (Consultas o Terapias) para"
              " revisar el desglose por tipo de servicio mensual:",
              style={
                  "fontSize": "11px",
                  "color": INK_SOFT,
                  "marginBottom": "10px",
              },
          ),
          dcc.Dropdown(
              id=ID_DROPDOWN_VAR_UBR,
              options=[{"label": v, "value": v} for v in variables_opciones],
              placeholder=(
                  "Selecciona una variable (muestra todas si está vacío)..."
              ),
              clearable=True,
              style={"fontSize": "12.5px", "fontFamily": FONT_SANS},
          ),
      ],
      style={
          "background": CARD,
          "border": f"1px solid {LINE}",
          "borderRadius": "8px",
          "borderTop": f"3px solid {VERDE}",
          "padding": "16px 18px",
          "marginBottom": "14px",
      },
  )

  tabla = dash_table.DataTable(
      id=ID_TABLA_DETALLE_UBR,
      columns=columnas,
      data=df_detalle[columnas_mostrar].to_dict("records"),
      sort_action="native",
      page_action="native",
      page_size=10,
      style_as_list_view=True,
      style_table={"overflowX": "auto"},
      style_header={
          "backgroundColor": GUINDA_DARK,
          "color": "#fff",
          "fontWeight": "700",
          "fontSize": "10.5px",
          "letterSpacing": ".04em",
          "textTransform": "uppercase",
          "textAlign": "left",
          "padding": "10px 14px",
          "border": "none",
      },
      style_cell={
          "fontFamily": FONT_SANS,
          "fontSize": "12.5px",
          "color": INK,
          "padding": "10px 14px",
          "textAlign": "left",
          "border": "none",
          "borderBottom": f"1px solid {LINE}",
      },
      style_data_conditional=[
          {"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"},
      ],
      css=[{"selector": ".dash-spreadsheet-menu", "rule": "display:none"}],
  )

  return html.Div([
      selector,
      html.Div(
          tabla,
          style={
              "background": CARD,
              "border": f"1px solid {LINE}",
              "borderRadius": "8px",
              "overflow": "hidden",
          },
      ),
  ])


@callback(
    Output(ID_TABLA_DETALLE_UBR, "data"), Input(ID_DROPDOWN_VAR_UBR, "value")
)
def _actualizar_tabla_detalle_ubr(variable_seleccionada):
  df_detalle = _cache_detalle_ubr["data"]
  if df_detalle.empty:
    return []
  if variable_seleccionada:
    df_detalle = df_detalle[df_detalle["VARIABLE"] == variable_seleccionada]
  return df_detalle.to_dict("records")


def analizar_unidad_basica_rehabilitacion(df):
  """Módulo operativo analizado desde Mes, actividad, Cantidad, Recaudación, Variable."""
  if df is None or df.empty:
    return dbc.Alert(
        "⚠️ El DataFrame de UBR llegó vacío al módulo operativo.",
        color="warning",
        className="m-3",
    )

  try:
    df_raw = df.copy()
    df_raw.columns = [str(c).strip().lower() for c in df_raw.columns]

    col_map = {}
    for c in df_raw.columns:
      if "mes" in c:
        col_map[c] = "MES"
      elif "activ" in c:
        col_map[c] = "ACTIVIDAD"
      elif "cant" in c:
        col_map[c] = "CANTIDAD"
      elif "recaud" in c:
        col_map[c] = "RECAUDACION"
      elif "variab" in c:
        col_map[c] = "VARIABLE"

    df_raw = df_raw.rename(columns=col_map)

    if not {"MES", "ACTIVIDAD", "CANTIDAD", "RECAUDACION", "VARIABLE"}.issubset(
        df_raw.columns
    ):
      return dbc.Alert(
          "❌ El archivo no contiene las columnas requeridas (Mes, actividad, Cantidad, Recaudación, Variable).",
          color="danger",
          className="m-3",
      )

    df_raw["CANTIDAD"] = pd.to_numeric(
        df_raw["CANTIDAD"], errors="coerce"
    ).fillna(0)
    df_raw["RECAUDACION"] = pd.to_numeric(
        df_raw["RECAUDACION"], errors="coerce"
    ).fillna(0)
    df_raw["ACTIVIDAD"] = (
        df_raw["ACTIVIDAD"].astype(str).str.strip().str.upper()
    )
    df_raw["VARIABLE"] = df_raw["VARIABLE"].astype(str).str.strip().str.title()
    df_raw["MES"] = df_raw["MES"].astype(str).str.strip().str.title()

    # ==========================================
    # CÁLCULOS DE KPIS (Orden Reacomodado)
    # ==========================================
    total_cantidad = df_raw["CANTIDAD"].sum()
    total_recaudacion = df_raw["RECAUDACION"].sum()

    df_terapias = df_raw[df_raw["VARIABLE"].str.contains("Terapia", case=False)]
    total_terapias = df_terapias["CANTIDAD"].sum()

    total_consultas = df_raw[
        df_raw["VARIABLE"].str.contains("Consulta", case=False)
    ]["CANTIDAD"].sum()

    kpis_row = dbc.Row([
        dbc.Col(
            _kpi_card(
                "ti-heart-handshake",
                "Total Servicios",
                f"{total_cantidad:,.0f}",
                "Suma global de atenciones",
                VERDE,
            ),
            width=12,
            sm=6,
            lg=3,
            className="mb-3",
        ),
        dbc.Col(
            _kpi_card(
                "ti-accessible",
                "Total Terapias",
                f"{total_terapias:,.0f}",
                "Atenciones en área de rehabilitación",
                VERDE,
            ),
            width=12,
            sm=6,
            lg=3,
            className="mb-3",
        ),
        dbc.Col(
            _kpi_card(
                "ti-stethoscope",
                "Consultas Generales",
                f"{total_consultas:,.0f}",
                "Atenciones médicas y psicológicas",
                GUINDA,
            ),
            width=12,
            sm=6,
            lg=3,
            className="mb-3",
        ),
        dbc.Col(
            _kpi_card(
                "ti-cash",
                "Recaudación Total",
                f"$ {total_recaudacion:,.2f}",
                "Cuotas de recuperación UBR",
                GUINDA,
            ),
            width=12,
            sm=6,
            lg=3,
            className="mb-3",
        ),
    ])

    month_order = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    if meses_cols_general := [
        m for m in month_order if m in df_raw["MES"].unique()
    ]:
      df_tendencia = df_raw.groupby("MES")["CANTIDAD"].sum().reset_index()
      fig_mensual = px.line(
          df_tendencia,
          x="MES",
          y="CANTIDAD",
          markers=True,
          color_discrete_sequence=[GUINDA],
          labels={"CANTIDAD": "Servicios Otorgados", "MES": ""},
      )
      fig_mensual.update_layout(
          margin=dict(l=40, r=15, t=10, b=15),
          plot_bgcolor="white",
          paper_bgcolor="white",
          height=260,
          yaxis={"gridcolor": "#f0f0f0", "tickfont": dict(color=INK_SOFT)},
          xaxis={"tickfont": dict(color=INK_SOFT)},
          font=dict(family="Inter, sans-serif"),
      )
      graph_tendencia = dcc.Graph(
          figure=fig_mensual,
          config={"displayModeBar": False, "responsive": True},
          style={"width": "100%"},
      )
    else:
      graph_tendencia = html.Div("ℹ️ No hay desglose mensual disponible.")

    # ==========================================
    # GRÁFICA DE PASTEL Y TABLITA RESUMEN
    # ==========================================
    df_pie = df_raw.groupby("VARIABLE")["CANTIDAD"].sum().reset_index()
    fig_pie = px.pie(
        df_pie,
        names="VARIABLE",
        values="CANTIDAD",
        hole=0.4,
        color_discrete_sequence=[VERDE, GUINDA],
    )
    fig_pie.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=220,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
        ),
        font=dict(family="Inter, sans-serif"),
    )
    graph_pie = dcc.Graph(
        figure=fig_pie,
        config={"displayModeBar": False, "responsive": True},
        style={"width": "100%"},
    )

    table_mini = dash_table.DataTable(
        columns=[
            {"name": "Clasificación", "id": "VARIABLE"},
            {"name": "Total", "id": "CANTIDAD"},
        ],
        data=df_pie.to_dict("records"),
        style_as_list_view=True,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": GUINDA_DARK,
            "color": "#fff",
            "fontWeight": "700",
            "fontSize": "10px",
            "textTransform": "uppercase",
            "padding": "6px 10px",
            "border": "none",
        },
        style_cell={
            "fontFamily": FONT_SANS,
            "fontSize": "11.5px",
            "color": INK,
            "padding": "6px 10px",
            "textAlign": "left",
            "border": "none",
            "borderBottom": f"1px solid {LINE}",
        },
    )

    panel_pie_con_tabla = html.Div([
        html.Div(graph_pie, style={"marginBottom": "10px"}),
        html.Div(
            table_mini,
            style={
                "background": CARD,
                "border": f"1px solid {LINE}",
                "borderRadius": "6px",
                "overflow": "hidden",
            },
        ),
    ])

    graficas_row = dbc.Row([
        dbc.Col(
            _chart_panel(
                "Evolución mensual de servicios UBR",
                graph_tendencia,
                color_top=GUINDA,
            ),
            md=6,
            className="mb-3",
        ),
        dbc.Col(
            _chart_panel(
                "Distribución Porcentual por Clasificación",
                panel_pie_con_tabla,
                color_top=VERDE,
            ),
            md=6,
            className="mb-3",
        ),
    ])

    # ==========================================
    # TABLA DETALLADA: Variable + Actividad + Meses
    # ==========================================
    df_pivot_act = df_raw.pivot_table(
        index=["VARIABLE", "ACTIVIDAD"],
        columns="MES",
        values="CANTIDAD",
        aggfunc="sum",
    ).reset_index()

    meses_cols = [m for m in month_order if m in df_pivot_act.columns]
    otros_meses = [
        c
        for c in df_pivot_act.columns
        if c not in meses_cols and c not in ["VARIABLE", "ACTIVIDAD"]
    ]
    meses_cols = meses_cols + otros_meses

    for m in meses_cols:
      df_pivot_act[m] = pd.to_numeric(df_pivot_act[m], errors="coerce").fillna(0)

    df_pivot_act["TOTAL"] = df_pivot_act[meses_cols].sum(axis=1)

    columnas_detalle = ["VARIABLE", "ACTIVIDAD"] + meses_cols + ["TOTAL"]
    df_detalle = df_pivot_act[columnas_detalle].copy()
    df_detalle = df_detalle.sort_values(
        by=["VARIABLE", "TOTAL"], ascending=[True, False]
    )

    etiquetas = {
        "VARIABLE": "Clasificación UBR",
        "ACTIVIDAD": "Tipo de Terapia / Consulta",
        "TOTAL": "Total",
    }
    for m in meses_cols:
      etiquetas[m] = m

    _cache_detalle_ubr["data"] = df_detalle
    panel_detalle = _tabla_detalle_ubr(df_detalle, columnas_detalle, etiquetas)

    return html.Div(
        [
            _fuentes_e_iconos(),
            _section_label("ti-chart-bar", "Resumen general UBR"),
            kpis_row,
            _section_label("ti-map-2", "Tendencias y distribución operativa"),
            graficas_row,
            _section_label("ti-table", "Registro detallado por tipo de servicio"),
            panel_detalle,
        ],
        style={
            "background": BG,
            "fontFamily": FONT_SANS,
            "color": INK,
            "padding": "5px",
        },
    )

  except Exception as e:
    return dbc.Alert(
        f"❌ Error al estructurar el cuadro de mando de UBR: {str(e)}",
        color="danger",
        className="m-3",
    )