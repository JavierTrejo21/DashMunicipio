# cb_navegacion.py
import io
import json
import math
import os
import re
import sqlite3
import traceback
import urllib.request

from fpdf import FPDF
import dash
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, dcc, html, no_update
import pandas as pd

from database import DB_GESTION, normalizar_nombre_tabla
from indicadores_pbr import calcular_indicadores_pbr

# Importaciones de componentes estéticos actualizados
from componentes_esteticos import (
    crear_tarjeta_estilo_acuerdo,
    generar_bloque_encabezado_area,
    generar_tabla_gestion,
)

# Importaciones de servicios MIR
from .servicio_mir import generar_resumen_indicadores_area

# --- Enrutador estratégico para conectar cada área con su archivo en 'areas/' ---
from analisis_estrategico import analizar_datos_estrategicos

# --- Renderizadores PDF específicos por área (réplica del dashboard en pantalla) ---
from areas_pdf import obtener_renderizador_pdf


def register_navegacion_callbacks(app):

  @app.callback(
      [
          Output("contenedor-botones-areas", "children"),
          Output("collapse-areas", "is_open"),
          Output("titulo-eje-seleccionado", "children"),
          Output("msg-placeholder-areas", "style"),
          Output("eje-id-seleccionado", "data"),
      ],
      [Input({"type": "tarjeta-eje", "index": ALL}, "n_clicks")],
      prevent_initial_call=True,
  )
  def desplegar_areas(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None):
      return no_update, no_update, no_update, no_update, no_update

    prop_id = ctx.triggered[0]["prop_id"]
    try:
      match_idx = re.search(r'"index":\s*(\d+)', prop_id)
      idx = int(match_idx.group(1)) if match_idx else None
    except Exception:
      return no_update, no_update, no_update, no_update, no_update

    if idx is None:
      return no_update, no_update, no_update, no_update, no_update

    conn = sqlite3.connect(DB_GESTION)
    eje_data = pd.read_sql_query(
        f"SELECT nombre FROM acuerdos WHERE id={idx}", conn
    )
    df_areas = pd.read_sql_query(
        f"SELECT * FROM areas WHERE acuerdo_id={idx}", conn
    )
    conn.close()

    nombre_eje = (
        eje_data.iloc[0]["nombre"] if not eje_data.empty else "Eje Desconocido"
    )

    if df_areas.empty:
      return (
          html.Small(
              "⚠️ No hay áreas asignadas a este eje.",
              className="text-muted p-3",
          ),
          True,
          nombre_eje,
          {"display": "none"},
          idx,
      )

    botones = []
    for _, area in df_areas.iterrows():
      botones.append(
          html.A(
              [
                  html.Div(
                      [html.I(className="bi bi-folder2-open")],
                      className="area-icon-v4",
                  ),
                  html.Span(
                      area["nombre"],
                      className="ms-2 fw-600",
                      style={"fontSize": "11.5px"},
                  ),
              ],
              id={"type": "btn-area", "index": area["id"]},
              className="area-row-v4",
              style={"textDecoration": "none", "cursor": "pointer"},
          )
      )

    return botones, True, nombre_eje, {"display": "none"}, idx

  @app.callback(
      [
          Output("contenido-area", "children"),
          Output("active-info", "data"),
          Output("resumen-kpis", "children"),
          Output("contenedor-tarjetas-acuerdos", "style"),
      ],
      [Input({"type": "btn-area", "index": ALL}, "n_clicks")],
      prevent_initial_call=True,
  )
  def mostrar_dashboard(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(x for x in n_clicks if x is not None):
      return no_update, no_update, no_update, no_update

    try:
      trigger_prop = ctx.triggered[0]["prop_id"]
      if not trigger_prop or "." not in trigger_prop:
        return no_update, no_update, no_update, no_update

      dict_str = trigger_prop.split(".")[0]
      dict_val = json.loads(dict_str)
      idx = dict_val.get("index")
    except Exception as parse_err:
      return (
          dbc.Alert(f"Error de selección: {str(parse_err)}", color="danger"),
          no_update,
          "",
          no_update,
      )

    if idx is None:
      return no_update, no_update, no_update, no_update

    conn = sqlite3.connect(DB_GESTION)
    query = """
            SELECT a.nombre as area_nom, ac.nombre as eje_nom 
            FROM areas a 
            JOIN acuerdos ac ON a.acuerdo_id = ac.id 
            WHERE a.id=?
        """
    area_info = pd.read_sql_query(query, conn, params=(idx,))

    if area_info.empty:
      conn.close()
      return (
          dbc.Alert("Área no registrada en la base de datos.", color="warning"),
          no_update,
          "",
          no_update,
      )

    nombre_completo = area_info.iloc[0]["area_nom"]
    nombre_eje = area_info.iloc[0]["eje_nom"]
    tabla = normalizar_nombre_tabla(nombre_completo)

    match_clave = re.match(r"^([\d\.]+)\s*(.*)", nombre_completo)
    clave_area = match_clave.group(1) if match_clave else ""
    nombre_area = match_clave.group(2) if match_clave else nombre_completo

    tablas_existentes = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    )["name"].tolist()

    icono_area = "ti ti-briefcase"
    if "psicologia" in nombre_completo.lower():
      icono_area = "ti ti-brain"
    elif "seguridad" in nombre_completo.lower():
      icono_area = "ti ti-shield"
    elif "obras" in nombre_completo.lower():
      icono_area = "ti ti-building"
    elif "dif" in nombre_completo.lower():
      icono_area = "ti ti-heart"

    if tabla not in tablas_existentes:
      conn.close()
      encabezado = generar_bloque_encabezado_area(
          nombre_eje, clave_area, nombre_area, icono_area
      )
      return (
          html.Div([
              encabezado,
              dbc.Alert(
                  "Aún no se han cargado datos para esta área administrativa.",
                  color="info",
                  className="mt-4",
              ),
          ]),
          {"tabla": tabla, "id": idx},
          "",
          no_update,
      )

    try:
      try:
        df = pd.read_sql_query(f'SELECT rowid, * FROM "{tabla}"', conn)
      except Exception:
        df = pd.read_sql_query(f'SELECT * FROM "{tabla}"', conn)
        if "rowid" not in df.columns:
          df.insert(0, "rowid", range(1, len(df) + 1))

      conn.close()

      try:
        resumen_mir = generar_resumen_indicadores_area(nombre_completo, df)
      except TypeError:
        try:
          resumen_mir = generar_resumen_indicadores_area(nombre_completo)
        except Exception:
          resumen_mir = html.Div()
      except Exception:
        resumen_mir = html.Div()

      analisis_especifico = analizar_datos_estrategicos(tabla, df)
      if analisis_especifico is None or isinstance(
          analisis_especifico, dbc.Alert
      ):
        analisis_especifico = analizar_datos_estrategicos(nombre_completo, df)

      if isinstance(analisis_especifico, dbc.Alert) and any(
          msg in str(analisis_especifico.children)
          for msg in ["aún no se ha configurado", "registrada correctamente"]
      ):
        analisis_especifico = html.Div()

      encabezado_v4 = generar_bloque_encabezado_area(
          nombre_eje, clave_area, nombre_area, icono_area
      )

      total_registros = len(df)

      total_invertido_str = "$ 0.00"
      for col_cand in df.columns:
        if any(
            term in col_cand.lower()
            for term in ["inversion", "monto", "costo", "total"]
        ):
          try:
            val_sum = pd.to_numeric(df[col_cand], errors="coerce").sum()
            if val_sum > 0:
              total_invertido_str = f"$ {val_sum:,.2f}"
              break
          except Exception:
            pass

      componente_tabla_detallada = html.Div([
          html.Div(
              children=dcc.Markdown(
                  """
<style>
.compact-table-wrapper table {
    width: 100% !important;
    table-layout: auto !important;
}
.compact-table-wrapper th {
    white-space: normal !important;
    word-break: break-word !important;
    text-align: center !important;
    padding: 8px 6px !important;
    font-size: 10.5px !important;
    line-height: 1.2 !important;
}
.compact-table-wrapper td {
    padding: 5px 6px !important;
    font-size: 11px !important;
}
</style>
                            """,
                  dangerously_allow_html=True,
              ),
              style={"display": "none"},
          ),
          html.Div(
              className="table-card mt-5",
              style={
                  "background": "#FFFFFF",
                  "border": "1px solid #E3DDD2",
                  "borderRadius": "8px",
                  "position": "relative",
                  "overflow": "hidden",
              },
              children=[
                  html.Div(
                      style={
                          "position": "absolute",
                          "top": "0",
                          "left": "0",
                          "right": "0",
                          "height": "3px",
                          "background": "#7A1E3D",
                          "zIndex": "2",
                      }
                  ),
                  html.Div(
                      id="btn-toggle-tabla-indicadores",
                      className="table-title-row",
                      style={
                          "display": "flex",
                          "alignItems": "center",
                          "justifyContent": "space-between",
                          "padding": "18px 22px",
                          "cursor": "pointer",
                          "userSelect": "none",
                      },
                      children=[
                          html.Div(
                              style={
                                  "display": "flex",
                                  "alignItems": "center",
                                  "gap": "10px",
                              },
                              children=[
                                  html.I(
                                      className="ti ti-table",
                                      style={
                                          "color": "#7A1E3D",
                                          "fontSize": "18px",
                                      },
                                  ),
                                  html.Div(
                                      "Registro de indicadores detallados",
                                      style={
                                          "fontFamily": (
                                              "'Playfair Display', serif"
                                          ),
                                          "fontWeight": "700",
                                          "fontSize": "16px",
                                          "letterSpacing": ".03em",
                                          "textTransform": "uppercase",
                                          "color": "#5A1530",
                                      },
                                  ),
                              ],
                          ),
                          html.I(
                              className="ti ti-chevron-down",
                              style={"color": "#6B625C", "fontSize": "16px"},
                          ),
                      ],
                  ),
                  dbc.Collapse(
                      html.Div(
                          className="compact-table-wrapper",
                          style={
                              "maxHeight": "310px",
                              "overflowY": "auto",
                              "overflowX": "auto",
                              "width": "100%",
                              "borderTop": "1px solid #E3DDD2",
                          },
                          children=[generar_tabla_gestion(df)],
                      ),
                      id="collapse-tabla-indicadores",
                      is_open=False,
                  ),
                  html.Div(
                      style={
                          "display": "flex",
                          "alignItems": "center",
                          "justifyContent": "space-between",
                          "padding": "12px 22px",
                          "borderTop": "1px solid #E3DDD2",
                          "fontSize": "11px",
                          "color": "#9B928C",
                          "background": "#FFF",
                      },
                      children=[
                          html.Span(f"{total_registros} registros"),
                          html.Span([
                              "Total invertido: ",
                              html.B(
                                  total_invertido_str,
                                  style={"color": "#0C5148"},
                              ),
                          ]),
                      ],
                  ),
              ],
          ),
      ])

      contenido = html.Div([
          encabezado_v4,
          html.Div(
              "Evidencia analítica de impacto social directo asociada a los"
              " objetivos institucionales.",
              className="section-desc",
          ),
          analisis_especifico,
          componente_tabla_detallada,
      ])

      return contenido, {"tabla": tabla, "id": idx}, "", no_update

    except Exception as e:
      traceback.print_exc()
      if "conn" in locals():
        conn.close()
      error_msg = (
          f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
      )
      return (
          dbc.Alert(
              f"Error interno al cargar la tabla '{tabla}': {error_msg}",
              color="danger",
          ),
          no_update,
          "",
          no_update,
      )

  def _texto_seguro(valor):
    """Convierte cualquier valor a texto y lo hace seguro para el motor
    de fuentes de FPDF (Latin-1), sustituyendo caracteres no soportados
    en lugar de reventar la generación del PDF."""
    try:
      texto = "" if valor is None or (isinstance(valor, float) and pd.isna(valor)) else str(valor)
    except Exception:
      texto = str(valor)
    return texto.encode("latin-1", "replace").decode("latin-1")

  def _agregar_encabezado_pdf(pdf, nombre_eje):
    pdf.add_page()
    pdf.set_fill_color(122, 30, 61)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 13)
    pdf.set_xy(10, 8)
    pdf.cell(0, 8, "REPORTE ESTRATÉGICO DE GESTIÓN", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"EJE: {_texto_seguro(nombre_eje).upper()}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(36)

  @app.callback(
      Output("download-reporte-eje", "data"),
      Input("btn-generar-pdf-eje", "n_clicks"),
      [
          State("titulo-eje-seleccionado", "children"),
          State("eje-id-seleccionado", "data"),
      ],
      prevent_initial_call=True,
  )
  def generar_pdf_eje(n_clicks, nombre_eje, eje_id_guardado):
    if not n_clicks or not nombre_eje:
      return no_update

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    _agregar_encabezado_pdf(pdf, nombre_eje)

    conn = sqlite3.connect(DB_GESTION)

    try:
      limpio_eje = str(nombre_eje).strip()
      eje_id = None
      nombre_eje_real = limpio_eje

      # --- 1. El id real del eje viene directo de la tarjeta que el
      # usuario clickeó (guardado en el Store "eje-id-seleccionado"),
      # que es EXACTAMENTE el mismo id que usa el panel en pantalla para
      # listar las áreas. Ya no se re-adivina buscando por nombre, porque
      # esa búsqueda por texto podía resolver a un id distinto al real
      # y por eso el PDF no encontraba áreas que sí se veían en pantalla.
      if eje_id_guardado is not None:
        eje_id = eje_id_guardado
        df_eje_nombre = pd.read_sql_query(
            "SELECT nombre FROM acuerdos WHERE id = ?", conn, params=(eje_id,)
        )
        if not df_eje_nombre.empty:
          nombre_eje_real = df_eje_nombre.iloc[0]["nombre"]

      # Respaldo por si el Store no llegó a poblarse (ej. sesión antigua):
      # se mantiene la búsqueda por nombre como red de seguridad.
      if eje_id is None:
        eje_query = (
            "SELECT id, nombre FROM acuerdos WHERE TRIM(nombre) = ? OR"
            " nombre LIKE ?"
        )
        df_eje = pd.read_sql_query(
            eje_query, conn, params=(limpio_eje, f"%{limpio_eje}%")
        )
        if df_eje.empty:
          palabras_clave = limpio_eje.split()[0]
          df_eje = pd.read_sql_query(
              "SELECT id, nombre FROM acuerdos WHERE nombre LIKE ?",
              conn,
              params=(f"%{palabras_clave}%",),
          )
        if not df_eje.empty:
          eje_id = df_eje.iloc[0]["id"]
          nombre_eje_real = df_eje.iloc[0]["nombre"]

      pdf.set_font("Arial", "B", 10)
      pdf.set_text_color(122, 30, 61)
      pdf.cell(0, 6, f"Eje validado en sistema: {_texto_seguro(nombre_eje_real)}", ln=True)
      pdf.set_text_color(0, 0, 0)
      pdf.ln(2)

      # --- 2. Traer TODAS las áreas vinculadas a ese acuerdo ---
      # Se compara castenado ambos lados a TEXTO: el id de "acuerdos" es
      # numérico, pero "areas.acuerdo_id" puede haberse guardado como texto
      # desde el <select> del modal (ej. "1" en vez de 1); comparar
      # directamente "=" perdía áreas por ese desfase de tipo.
      df_areas = pd.DataFrame()
      if eje_id is not None:
        df_areas = pd.read_sql_query(
            "SELECT * FROM areas WHERE TRIM(CAST(acuerdo_id AS TEXT)) ="
            " TRIM(CAST(? AS TEXT))",
            conn,
            params=(eje_id,),
        )

      # Respaldo: si por algún motivo no hubo match por id, buscar por
      # texto del nombre del eje directamente en la tabla de áreas.
      if df_areas.empty:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(areas)")
        columnas_areas = [col[1] for col in cursor.fetchall()]
        for col_texto in ["nombre_eje", "eje", "acuerdo", "eje_nombre", "nombre_acuerdo"]:
          if col_texto in columnas_areas:
            df_areas = pd.read_sql_query(
                f'SELECT * FROM areas WHERE "{col_texto}" LIKE ?',
                conn,
                params=(f"%{nombre_eje_real}%",),
            )
            if not df_areas.empty:
              break

      if "nombre" in df_areas.columns:
        df_areas = df_areas.sort_values("nombre")

      if df_areas.empty:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(
            0,
            10,
            "No se encontraron áreas vinculadas a este eje en la base de"
            " datos.",
            ln=True,
        )
      else:
        pdf.set_font("Arial", "I", 9)
        pdf.cell(
            0, 6, f"Áreas institucionales detectadas: {len(df_areas)}", ln=True
        )
        pdf.ln(3)

        ancho_pagina = pdf.w - pdf.l_margin - pdf.r_margin

        # --- 3. Por cada área, imprimir el detalle COMPLETO (todas las
        # filas y todas las columnas de su tabla, sin recortes) ---
        for _, area in df_areas.iterrows():
          nombre_area_txt = area["nombre"] if "nombre" in area else "Área Operativa"

          if pdf.get_y() > 250:
            pdf.add_page()

          pdf.set_font("Arial", "B", 10)
          pdf.set_fill_color(240, 235, 230)
          pdf.set_draw_color(181, 137, 44)
          pdf.set_line_width(0.3)
          pdf.cell(
              0,
              7,
              f" ÁREA: {_texto_seguro(nombre_area_txt).upper()}",
              border=1,
              ln=True,
              fill=True,
          )
          pdf.ln(2)

          tabla_nom = normalizar_nombre_tabla(nombre_area_txt)
          try:
            df_datos = pd.read_sql_query(f'SELECT * FROM "{tabla_nom}"', conn)
            columnas_datos = [c for c in df_datos.columns if str(c).lower() not in ["rowid", "id"]]

            renderizador_especifico = obtener_renderizador_pdf(nombre_area_txt)

            if renderizador_especifico is not None:
              # --- Réplica exacta del dashboard en pantalla para esta
              # área (tarjetas KPI, barras de progreso, gráfica mensual
              # y tabla), usando el mismo cálculo que su módulo en
              # areas/<area>.py ---
              try:
                renderizador_especifico(pdf, df_datos, ancho_pagina)
              except Exception as e_render:
                pdf.set_font("Arial", "I", 8)
                pdf.set_text_color(180, 60, 60)
                pdf.multi_cell(
                    ancho_pagina, 5,
                    _texto_seguro(f"  (Error al generar el panel específico de esta área: {e_render}. Se muestra el detalle genérico.)"),
                )
                pdf.set_text_color(0, 0, 0)
                renderizador_especifico = None  # fuerza el fallback abajo

            if renderizador_especifico is None:
              pdf.set_font("Arial", "", 8)
              pdf.cell(0, 5, f"Total de registros: {len(df_datos)}", ln=True)

              inversion_total = 0
              for col in columnas_datos:
                if any(term in str(col).lower() for term in ["inversion", "monto", "costo", "total", "recaudac"]):
                  try:
                    inversion_total += pd.to_numeric(df_datos[col], errors="coerce").sum()
                  except Exception:
                    pass

              if inversion_total > 0:
                pdf.cell(0, 5, f"Inversión / Monto global registrado: $ {inversion_total:,.2f}", ln=True)

              pdf.ln(1)

              if df_datos.empty or not columnas_datos:
                pdf.set_font("Arial", "I", 8)
                pdf.set_text_color(120, 120, 120)
                pdf.cell(0, 5, "  (No hay registros cargados en esta área)", ln=True)
                pdf.set_text_color(0, 0, 0)
              else:
                # Detalle completo: cada registro con TODAS sus columnas,
                # en formato "columna: valor" con salto de línea automático.
                for num_fila, (_, fila) in enumerate(df_datos.iterrows(), start=1):
                  if pdf.get_y() > 265:
                    pdf.add_page()

                  pdf.set_font("Arial", "B", 8)
                  pdf.set_text_color(122, 30, 61)
                  pdf.cell(0, 5, f"Registro {num_fila}", ln=True)
                  pdf.set_text_color(0, 0, 0)
                  pdf.set_font("Arial", "", 8)

                  for col in columnas_datos:
                    val = fila[col]
                    if pd.isna(val) or str(val).strip() == "":
                      continue
                    if pdf.get_y() > 270:
                      pdf.add_page()
                    texto_linea = _texto_seguro(f"  • {col}: {val}")
                    pdf.multi_cell(ancho_pagina, 4.5, texto_linea)

                  pdf.ln(1.5)

            pdf.ln(3)
          except Exception as e_area:
            pdf.set_font("Arial", "I", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.multi_cell(
                ancho_pagina,
                5,
                _texto_seguro(f"  (Sin tabla de datos cargada para esta área: {e_area})"),
            )
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)

    except Exception as e:
      pdf.set_font("Arial", "", 9)
      pdf.multi_cell(0, 8, _texto_seguro(f"Error al procesar datos del eje: {e}"))
    finally:
      conn.close()

    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(
        0,
        10,
        "Sistema de Gestión Municipal - Reporte Estratégico Consolidado",
        align="C",
    )

    pdf_output = pdf.output(dest="S")
    pdf_bytes = (
        bytes(pdf_output) if not isinstance(pdf_output, bytes) else pdf_output
    )

    nombre_archivo_seguro = re.sub(r"[^A-Za-z0-9_]+", "_", str(nombre_eje)).strip("_")
    return dcc.send_bytes(pdf_bytes, f"Reporte_Eje_{nombre_archivo_seguro}.pdf")

  @app.callback(
      Output("collapse-tabla-indicadores", "is_open"),
      Input("btn-toggle-tabla-indicadores", "n_clicks"),
      State("collapse-tabla-indicadores", "is_open"),
      prevent_initial_call=True,
  )
  def alternar_tabla_indicadores(n_clicks, is_open):
    if n_clicks:
      return not is_open
    return is_open

  @app.callback(
      [
          Output("contenido-area", "children", allow_duplicate=True),
          Output("resumen-kpis", "children", allow_duplicate=True),
          Output("collapse-areas", "is_open", allow_duplicate=True),
          Output("contenedor-tarjetas-acuerdos", "style", allow_duplicate=True),
      ],
      Input("btn-volver-ejes", "n_clicks"),
      prevent_initial_call=True,
  )
  def volver_a_ejes(n):
    if n:
      return "", "", False, no_update
    return no_update, no_update, no_update, no_update