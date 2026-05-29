import pandas as pd
from visualizaciones import generar_tablero_impacto
from visualizaciones_especificas import renderizar_pueblos_indigenas

def obtener_tablero_por_area(nombre_area, df):
    # Convertimos a mayúsculas para evitar errores de dedo
    area = str(nombre_area).upper()
    
    if "PUEBLOS INDIGENAS" in area:
        return renderizar_pueblos_indigenas(df)
    
    # Si no es un área especial, retorna el general que ya tenías
    return generar_tablero_impacto(df)
