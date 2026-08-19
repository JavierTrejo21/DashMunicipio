# areas_pdf.py
import pandas as pd


def renderizador_ejemplo_area(pdf, df_datos, ancho_pagina):
  """Ejemplo de renderizador específico para un área particular.

  Puedes replicar esta estructura para crear vistas de PDF personalizadas por
  área.
  """
  pdf.set_font("Arial", "B", 9)
  pdf.set_text_color(122, 30, 61)
  pdf.cell(
      0,
      6,
      "Resumen Ejecutivo Específico (Generado por areas_pdf.py)",
      ln=True,
  )
  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Arial", "", 8)
  pdf.cell(
      0, 5, f"Registros totales procesados en vista dedicada: {len(df_datos)}", ln=True
  )
  pdf.ln(2)


# Diccionario que mapea nombres de áreas (o palabras clave) con su función renderizadora específica
# Puedes agregar funciones personalizadas y asociarlas a nombres clave de tus áreas.
MAPEO_RENDERIZADORES = {
    # Ejemplo: "dif municipal": renderizador_dif_municipal,
    # Ejemplo: "obras publicas": renderizador_obras_publicas,
}


def obtener_renderizador_pdf(nombre_area):
  """Busca y retorna una función renderizadora específica según el nombre del área.

  Si no encuentra ninguna coincidencia, retorna None para que el sistema
  aplique el formato genérico estándar.
  """
  if not nombre_area:
    return None

  nombre_lower = str(nombre_area).lower()

  # Buscar coincidencias por palabras clave en el nombre del área
  for clave, renderizador in MAPEO_RENDERIZADORES.items():
    if clave in nombre_lower:
      return renderizador

  # Por defecto retorna None (activa el renderizador genérico en cb_navegacion.py)
  return None
