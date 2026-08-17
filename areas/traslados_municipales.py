import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dash_table, dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import unicodedata

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

POBLACION_TOTAL_MUNICIPIO = 22903

# Variable global interna para mantener el DataFrame limpio disponible para el callback
_df_traslados_cache = None


def limpiar_texto(texto):
  if not isinstance(texto, str):
    return str(texto)
  nfkd_form = unicodedata.normalize("NFKD", texto)
  return "".join(
      [c for c in nfkd_form if not unicodedata.combining(c)]
  ).upper().strip()


# ==========================================================
# BLOQUES DE LAYOUT
# ==========================================================


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


def _chart_panel(titulo, fig, color_top=GUINDA):
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
          dcc.Graph(
              figure=fig,
              config={"displayModeBar": False, "responsive": True},
              style={"width": "100%"},
          ),
      ],
      style={
          "background": CARD,
          "border": f"1px solid {LINE}",
          "borderRadius": "8px",
          "borderTop": f"3px solid {color_top}",
          "padding": "16px 18px 8px",
          "overflow": "hidden",
          "height": "100%",
          "boxSizing": "border-box",
      },
  )


# ==========================================================
# MÓDULO OPERATIVO — TRASLADOS MUNICIPALES (DIF)
# ==========================================================


def analizar_traslados_municipales(df):
  """Módulo operativo — 2.11 Traslados Municipales con desglose de edad y género."""
  global _df_traslados_cache

  if df is None or df.empty:
    return dbc.Alert(
        "⚠️ El archivo de Traslados Municipales no contiene registros"
        " válidos.",
        color="danger",
        className="m-3",
    )

  try:
    df_clean = df.copy()
    df_clean.columns = [str(c).strip() for c in df_clean.columns]

    col_mes = next((c for c in df_clean.columns if "MES" in c.upper()), "mes")
    col_loc = next(
        (
            c
            for c in df_clean.columns
            if "LOCALIDAD" in c.upper() or "BARRIO" in c.upper()
        ),
        "Barrio/Localidad",
    )
    col_masc = next(
        (
            c
            for c in df_clean.columns
            if "MASCULINO" in c.upper() or "HOMBRE" in c.upper()
        ),
        "Masculino",
    )
    col_fem = next(
        (
            c
            for c in df_clean.columns
            if "FEMENINO" in c.upper() or "MUJER" in c.upper()
        ),
        "Femenino",
    )

    col_ninos = next(
        (c for c in df_clean.columns if "0" in c and "18" in c), "0 - 18 Años"
    )
    col_jovenes = next(
        (c for c in df_clean.columns if "18" in c and "29" in c), "18-29 Años"
    )
    col_adultos = next(
        (c for c in df_clean.columns if "30" in c or "MAS" in c.upper()),
        "Mas de 30 años",
    )

    df_limpio = pd.DataFrame()
    df_limpio["Mes"] = (
        df_clean[col_mes].astype(str).str.strip().str.capitalize()
    )
    df_limpio["Comunidad"] = (
        df_clean[col_loc].astype(str).str.strip().str.title()
    )
    df_limpio["Masculino"] = (
        pd.to_numeric(df_clean[col_masc], errors="coerce").fillna(0).astype(int)
    )
    df_limpio["Femenino"] = (
        pd.to_numeric(df_clean[col_fem], errors="coerce").fillna(0).astype(int)
    )
    df_limpio["0-18 Años"] = (
        pd.to_numeric(df_clean[col_ninos], errors="coerce").fillna(0).astype(int)
    )
    df_limpio["18-29 Años"] = (
        pd.to_numeric(df_clean[col_jovenes], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df_limpio["Más de 30 Años"] = (
        pd.to_numeric(df_clean[col_adultos], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df_limpio["Total"] = df_limpio["Masculino"] + df_limpio["Femenino"]

    _df_traslados_cache = df_limpio.copy()

    total_general = df_limpio["Total"].sum()
    comunidades_disponibles = sorted(df_limpio["Comunidad"].unique())

    enfoque_card = html.Div(
        [
            html.Div(
                [
                    html.I(
                        className="ti ti-info-circle",
                        style={"fontSize": "15px", "color": VERDE},
                    ),
                    html.Span(
                        "Enfoque del programa de traslados municipales",
                        style={
                            "fontFamily": FONT_SERIF,
                            "fontWeight": "700",
                            "fontSize": "13px",
                            "letterSpacing": ".04em",
                            "color": GUINDA_DARK,
                            "textTransform": "uppercase",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "borderBottom": f"1px solid {LINE}",
                    "paddingBottom": "10px",
                    "marginBottom": "12px",
                },
            ),
            html.P(
                "El servicio de traslados municipales coordina el apoyo de"
                " transporte para ciudadanos que requieren atención médica,"
                " trámites o gestiones fuera de sus localidades hacia centros"
                " de salud y oficinas administrativas.",
                style={
                    "fontSize": "13px",
                    "color": INK,  # <- Corregido a color oscuro principal para máxima legibilidad
                    "lineHeight": "1.6",
                    "marginBottom": "12px",
                    "fontWeight": "400",
                },
            ),
            html.Ul(
                [
                    html.Li(
                        "Atención y cobertura de traslados a las diferentes"
                        " comunidades y cabecera municipal.",
                        style={
                            "fontSize": "12.5px",
                            "color": (
                                INK
                            ),  # <- Corregido a color oscuro principal
                            "marginBottom": "6px",
                        },
                    ),
                    html.Li(
                        "Registro desglosado por género y rangos de edad"
                        " para control estadístico operativo.",
                        style={
                            "fontSize": "12.5px",
                            "color": (
                                INK
                            ),  # <- Corregido a color oscuro principal
                            "marginBottom": "6px",
                        },
                    ),
                    html.Li(
                        f"Volumen general acumulado en el periodo: {total_general:,}"
                        " servicios de traslado registrados.",
                        style={
                            "fontSize": "12.5px",
                            "color": (
                                INK
                            ),  # <- Corregido a color oscuro principal
                            "fontWeight": "600",
                        },
                    ),
                ],
                style={"paddingLeft": "18px", "margin": "0"},
            ),
        ],
        style={
            "background": CARD,
            "border": f"1px solid {LINE}",
            "borderRadius": "8px",
            "borderTop": f"3px solid {VERDE}",
            "padding": "16px 20px",
            "boxShadow": "0 1px 2px rgba(84,19,42,.05)",
        },
    )

    kpis_row = dbc.Row([
        dbc.Col(
            _kpi_card(
                "ti-users",
                "Total de Ciudadanos Atendidos",
                f"{total_general:,} Beneficiarios",
                "Ciudadanos trasladados a diferentes instancias de Salud",
                GUINDA,
            ),
            width=12,
            md=4,
            className="mb-3",
        ),
        dbc.Col(
            _kpi_card(
                "ti-calendar-event",
                "Total de Traslados programados",
                "1,114 servicios",
                "Traslados programados con anticipación",
                VERDE,
            ),
            width=12,
            md=4,
            className="mb-3",
        ),
        dbc.Col(
            _kpi_card(
                "ti-alert-octagon",
                "Atención a emergencias",
                "368 servicios",
                "Respuesta inmediata a solicitudes de traslado de urgencia",
                VERDE,
            ),
            width=12,
            md=4,
            className="mb-3",
        ),
    ])

    orden_meses = [
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
    df_meses = df_limpio.groupby("Mes", as_index=False)["Total"].sum()
    df_meses["Mes_Ord"] = pd.Categorical(
        df_meses["Mes"], categories=orden_meses, ordered=True
    )
    df_meses = df_meses.sort_values("Mes_Ord").dropna(subset=["Mes_Ord"])
    promedio_mensual = df_meses["Total"].mean() if not df_meses.empty else 0

    fig_lineas = go.Figure()
    fig_lineas.add_trace(
        go.Scatter(
            x=df_meses["Mes"],
            y=df_meses["Total"],
            mode="lines+markers+text",
            name="Traslados",
            line=dict(color=VERDE, width=3),
            marker=dict(size=8, color=GUINDA),
            text=df_meses["Total"].apply(lambda x: f"{int(x):,}"),
            textposition="top center",
            textfont=dict(family="Inter, sans-serif", size=10, color=INK_SOFT),
        )
    )

    if not df_meses.empty:
      fig_lineas.add_hline(
          y=promedio_mensual,
          line_dash="dash",
          line_color=GUINDA,
          line_width=2,
          annotation_text=f"Promedio: {promedio_mensual:,.2f}",
          annotation_position="bottom right",
          annotation_font=dict(
              size=10, color=GUINDA, family="Inter, sans-serif"
          ),
      )

    fig_lineas.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=50, l=40, r=20),
        height=350,
        xaxis=dict(
            showgrid=True,
            gridcolor=LINE,
            tickangle=-25,
            tickfont=dict(color=INK_SOFT, family="Inter, sans-serif"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=LINE,
            rangemode="tozero",
            tickfont=dict(color=INK_SOFT, family="Inter, sans-serif"),
        ),
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
    )

    seccion_grafica = _chart_panel(
        "Histórico mensual y línea de promedio de traslados",
        fig_lineas,
        color_top=VERDE,
    )

    df_tabla_meses = df_meses[["Mes", "Total"]].copy()
    df_tabla_meses.columns = ["Mes", "Servicios"]

    if not df_tabla_meses.empty:
      fila_promedio = pd.DataFrame(
          [{"Mes": "Promedio", "Servicios": promedio_mensual}]
      )
      df_tabla_meses_con_promedio = pd.concat(
          [df_tabla_meses, fila_promedio], ignore_index=True
      )
    else:
      df_tabla_meses_con_promedio = df_tabla_meses.copy()

    df_tabla_meses_con_promedio["Servicios_Fmt"] = df_tabla_meses_con_promedio[
        "Servicios"
    ].apply(lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{int(x):,}")

    max_val = df_tabla_meses["Servicios"].max() if not df_tabla_meses.empty else 0
    min_val = df_tabla_meses["Servicios"].min() if not df_tabla_meses.empty else 0

    tabla_meses_lat = dash_table.DataTable(
        data=df_tabla_meses_con_promedio[
            ["Mes", "Servicios_Fmt"]
        ].to_dict("records"),
        columns=[
            {"name": "Mes", "id": "Mes"},
            {"name": "Servicios", "id": "Servicios_Fmt"},
        ],
        fixed_rows={"headers": True},
        style_table={
            "overflowX": "auto",
            "overflowY": "auto",
            "maxHeight": "290px",
        },
        style_header={
            "backgroundColor": GUINDA_DARK,
            "color": "#ffffff",
            "fontWeight": "700",
            "textAlign": "center",
            "fontSize": "10.5px",
            "letterSpacing": ".04em",
            "textTransform": "uppercase",
            "border": "none",
            "fontFamily": "Inter, sans-serif",
            "padding": "10px 14px",
        },
        style_cell={
            "textAlign": "left",
            "padding": "10px 14px",
            "fontSize": "12px",
            "fontFamily": "Inter, sans-serif",
            "color": INK,
            "borderBottom": f"1px solid {LINE}",
            "backgroundColor": CARD,
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"},
            {
                "if": {
                    "filter_query": (
                        f"{{Servicios_Fmt}} = '{int(max_val):,}'"
                        if max_val
                        else "none"
                    ),
                    "column_id": "Servicios_Fmt",
                },
                "backgroundColor": VERDE_LIGHT,
                "color": VERDE_DARK,
                "fontWeight": "bold",
            },
            {
                "if": {
                    "filter_query": (
                        f"{{Servicios_Fmt}} = '{int(min_val):,}'"
                        if min_val
                        else "none"
                    ),
                    "column_id": "Servicios_Fmt",
                },
                "backgroundColor": GUINDA_LIGHT,
                "color": GUINDA_DARK,
                "fontWeight": "bold",
            },
            {
                "if": {"row_index": len(df_tabla_meses)},
                "backgroundColor": "#EFECE6",
                "fontWeight": "bold",
                "color": GUINDA_DARK,
            },
        ],
    )

    panel_tabla_lat = html.Div(
        [
            html.Div(
                "Detalle por mes, máximo, mínimo y promedio",
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": ".03em",
                    "textTransform": "uppercase",
                    "color": INK_SOFT,
                    "marginBottom": "10px",
                },
            ),
            html.Div(
                tabla_meses_lat,
                style={
                    "background": CARD,
                    "border": f"1px solid {LINE}",
                    "borderRadius": "8px",
                    "overflow": "hidden",
                },
            ),
        ],
        style={
            "background": CARD,
            "border": f"1px solid {LINE}",
            "borderRadius": "8px",
            "borderTop": f"3px solid {GUINDA}",
            "padding": "16px 18px 8px",
            "height": "100%",
            "boxSizing": "border-box",
        },
    )

    fila_tendencia_y_tabla = dbc.Row([
        dbc.Col(panel_tabla_lat, width=12, lg=4, className="mb-3 mb-lg-0"),
        dbc.Col(seccion_grafica, width=12, lg=8),
    ])

    df_tabla_inicial = df_limpio[["Comunidad", "Mes", "Total"]].copy()

    tabla_detallada = dash_table.DataTable(
        id="tabla-comunidades-traslados",
        data=df_tabla_inicial.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df_tabla_inicial.columns],
        page_size=7,
        style_table={
            "overflowX": "auto",
            "overflowY": "auto",
            "maxHeight": "280px",
        },
        style_header={
            "backgroundColor": GUINDA_DARK,
            "color": "#ffffff",
            "fontWeight": "700",
            "textAlign": "center",
            "fontSize": "10.5px",
            "letterSpacing": ".04em",
            "textTransform": "uppercase",
            "border": "none",
            "fontFamily": "Inter, sans-serif",
            "padding": "10px 14px",
        },
        style_cell={
            "textAlign": "left",
            "padding": "10px 14px",
            "fontSize": "12px",
            "fontFamily": "Inter, sans-serif",
            "color": INK,
            "borderBottom": f"1px solid {LINE}",
            "backgroundColor": CARD,
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#FAF8F4"},
        ],
        sort_action="native",
    )

    panel_tabla_compacta = html.Div(
        [
            html.Div(
                "Registro por Comunidad y Mes",
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": ".03em",
                    "textTransform": "uppercase",
                    "color": INK_SOFT,
                    "marginBottom": "10px",
                },
            ),
            html.Div(
                tabla_detallada,
                style={
                    "background": CARD,
                    "border": f"1px solid {LINE}",
                    "borderRadius": "8px",
                    "overflow": "hidden",
                },
            ),
        ],
        style={
            "background": CARD,
            "border": f"1px solid {LINE}",
            "borderRadius": "8px",
            "borderTop": f"3px solid {GUINDA}",
            "padding": "16px 18px 8px",
            "height": "100%",
            "boxSizing": "border-box",
        },
    )

    total_masc_gen = df_limpio["Masculino"].sum()
    total_fem_gen = df_limpio["Femenino"].sum()
    fig_pastel_init = px.pie(
        names=["Masculino", "Femenino"],
        values=[total_masc_gen, total_fem_gen],
        color_discrete_sequence=[VERDE, GUINDA],
        hole=0.4,
    )
    fig_pastel_init.update_traces(
        textinfo="label+percent+value", textfont_size=11
    )
    fig_pastel_init.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
        ),
        font=dict(family="Inter, sans-serif"),
    )

    panel_pastel = html.Div(
        [
            html.Div(
                "Relación por Género (Masculino / Femenino)",
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": ".03em",
                    "textTransform": "uppercase",
                    "color": INK_SOFT,
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(
                id="grafica-pastel-genero-traslados",
                figure=fig_pastel_init,
                config={"displayModeBar": False, "responsive": True},
                style={"width": "100%"},
            ),
        ],
        style={
            "background": CARD,
            "border": f"1px solid {LINE}",
            "borderRadius": "8px",
            "borderTop": f"3px solid {VERDE}",
            "padding": "16px 18px 8px",
            "height": "100%",
            "boxSizing": "border-box",
        },
    )

    tot_ninos = df_limpio["0-18 Años"].sum()
    tot_jovenes = df_limpio["18-29 Años"].sum()
    tot_adultos = df_limpio["Más de 30 Años"].sum()
    suma_edades = (
        (tot_ninos + tot_jovenes + tot_adultos)
        if (tot_ninos + tot_jovenes + tot_adultos) > 0
        else 1
    )

    textos_edades = [
        (
            f"{tot_ninos:,} ({(tot_ninos/suma_edades)*100:.1f}%)"
            if tot_ninos > 0
            else "0"
        ),
        (
            f"{tot_jovenes:,} ({(tot_jovenes/suma_edades)*100:.1f}%)"
            if tot_jovenes > 0
            else "0"
        ),
        (
            f"{tot_adultos:,} ({(tot_adultos/suma_edades)*100:.1f}%)"
            if tot_adultos > 0
            else "0"
        ),
    ]

    fig_edades_init = px.bar(
        x=["0 - 18 Años", "18-29 Años", "Más de 30 Años"],
        y=[tot_ninos, tot_jovenes, tot_adultos],
        text=textos_edades,
        color_discrete_sequence=[VERDE],
    )
    fig_edades_init.update_traces(
        textposition="auto", textfont=dict(size=11, color="#fff")
    )
    fig_edades_init.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=INK_SOFT, family="Inter, sans-serif"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=LINE,
            rangemode="tozero",
            tickfont=dict(color=INK_SOFT, family="Inter, sans-serif"),
        ),
        font=dict(family="Inter, sans-serif"),
    )

    panel_edades = html.Div(
        [
            html.Div(
                "Distribución por Rangos de Edad",
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": ".03em",
                    "textTransform": "uppercase",
                    "color": INK_SOFT,
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(
                id="grafica-barras-edades-traslados",
                figure=fig_edades_init,
                config={"displayModeBar": False, "responsive": True},
                style={"width": "100%"},
            ),
        ],
        style={
            "background": CARD,
            "border": f"1px solid {LINE}",
            "borderRadius": "8px",
            "borderTop": f"3px solid {GUINDA}",
            "padding": "16px 18px 8px",
            "height": "100%",
            "boxSizing": "border-box",
        },
    )

    filtro_seccion = html.Div([
        html.Div(
            [
                html.Div(
                    [
                        html.I(
                            className="ti ti-filter",
                            style={"color": VERDE, "fontSize": "15px"},
                        ),
                        html.Span(
                            "Consulta detallada por comunidad",
                            style={
                                "fontFamily": FONT_SERIF,
                                "fontWeight": "700",
                                "fontSize": "13px",
                                "letterSpacing": ".04em",
                                "color": GUINDA_DARK,
                                "textTransform": "uppercase",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "8px",
                        "marginBottom": "8px",
                    },
                ),
                html.P(
                    "Selecciona o busca una comunidad para filtrar los registros"
                    " de la tabla y actualizar las gráficas de género y edad:",
                    style={
                        "fontSize": "12px",
                        "color": INK_SOFT,
                        "marginBottom": "10px",
                    },
                ),
                dcc.Dropdown(
                    id="dropdown-filtro-comunidad-traslados",
                    options=[
                        {"label": c, "value": c} for c in comunidades_disponibles
                    ],
                    placeholder=(
                        "Selecciona una comunidad (muestra todos si está"
                        " vacío)..."
                    ),
                    clearable=True,
                    style={"fontSize": "13px", "fontFamily": FONT_SANS},
                ),
            ],
            style={
                "background": CARD,
                "border": f"1px solid {LINE}",
                "borderRadius": "8px",
                "borderTop": f"3px solid {VERDE}",
                "padding": "16px 18px",
                "marginBottom": "16px",
            },
        ),
        dbc.Row([
            dbc.Col(panel_tabla_compacta, width=12, lg=4, className="mb-3 mb-lg-0"),
            dbc.Col(panel_pastel, width=12, lg=4, className="mb-3 mb-lg-0"),
            dbc.Col(panel_edades, width=12, lg=4),
        ]),
    ])

    return html.Div(
        [
            _fuentes_e_iconos(),
            _section_label("ti-info-circle", "Enfoque del programa"),
            enfoque_card,
            _section_label("ti-chart-bar", "Resumen general"),
            kpis_row,
            _section_label("ti-chart-line", "Comportamiento e histórico"),
            fila_tendencia_y_tabla,
            _section_label("ti-map-pin", "Detalle por comunidad"),
            filtro_seccion,
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
        f"❌ Error al estructurar el cuadro de mando de Traslados Municipales:"
        f" {str(e)}",
        color="danger",
        className="m-3",
    )


@callback(
    [
        Output("tabla-comunidades-traslados", "data"),
        Output("grafica-pastel-genero-traslados", "figure"),
        Output("grafica-barras-edades-traslados", "figure"),
    ],
    Input("dropdown-filtro-comunidad-traslados", "value"),
)
def filtrar_tabla_y_graficas_traslados(comunidad_seleccionada):
  global _df_traslados_cache
  if _df_traslados_cache is None or _df_traslados_cache.empty:
    return [], go.Figure(), go.Figure()

  df_filtrado = _df_traslados_cache.copy()

  if comunidad_seleccionada:
    df_filtrado = df_filtrado[
        df_filtrado["Comunidad"] == comunidad_seleccionada
    ]

  df_tabla = df_filtrado[["Comunidad", "Mes", "Total"]].copy()

  total_masc = df_filtrado["Masculino"].sum()
  total_fem = df_filtrado["Femenino"].sum()

  fig_pastel = px.pie(
      names=["Masculino", "Femenino"],
      values=[total_masc, total_fem],
      color_discrete_sequence=[VERDE, GUINDA],
      hole=0.4,
  )
  fig_pastel.update_traces(
      textinfo="label+percent+value", textfont_size=11
  )
  fig_pastel.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      margin=dict(t=20, b=20, l=20, r=20),
      height=280,
      legend=dict(
          orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
      ),
      font=dict(family="Inter, sans-serif"),
  )

  tot_ninos = df_filtrado["0-18 Años"].sum()
  tot_jovenes = df_filtrado["18-29 Años"].sum()
  tot_adultos = df_filtrado["Más de 30 Años"].sum()
  suma_edades = (
      (tot_ninos + tot_jovenes + tot_adultos)
      if (tot_ninos + tot_jovenes + tot_adultos) > 0
      else 1
  )

  textos_edades = [
      (
          f"{tot_ninos:,} ({(tot_ninos/suma_edades)*100:.1f}%)"
          if tot_ninos > 0
          else "0"
      ),
      (
          f"{tot_jovenes:,} ({(tot_jovenes/suma_edades)*100:.1f}%)"
          if tot_jovenes > 0
          else "0"
      ),
      (
          f"{tot_adultos:,} ({(tot_adultos/suma_edades)*100:.1f}%)"
          if tot_adultos > 0
          else "0"
      ),
  ]

  fig_edades = px.bar(
      x=["0 - 18 Años", "18-29 Años", "Más de 30 Años"],
      y=[tot_ninos, tot_jovenes, tot_adultos],
      text=textos_edades,
      color_discrete_sequence=[VERDE],
  )
  fig_edades.update_traces(
      textposition="auto", textfont=dict(size=11, color="#fff")
  )
  fig_edades.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      margin=dict(t=20, b=20, l=20, r=20),
      height=280,
      xaxis=dict(
          showgrid=False,
          tickfont=dict(color=INK_SOFT, family="Inter, sans-serif"),
      ),
      yaxis=dict(
          showgrid=True,
          gridcolor=LINE,
          rangemode="tozero",
          tickfont=dict(color=INK_SOFT, family="Inter, sans-serif"),
      ),
      font=dict(family="Inter, sans-serif"),
  )

  return df_tabla.to_dict("records"), fig_pastel, fig_edades