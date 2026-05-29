import pandas as pd

def calcular_indicadores_pbr(df):
    """
    Analiza el DataFrame del área bajo el enfoque operativo (Alternativa A).
    Si no hay metas programadas, evalúa el volumen acumulado de gestión ciudadana.
    """
    resultado = {
        "porcentaje_cumplimiento": 0.0,
        "total_metas_programadas": 0,
        "total_metas_alcanzadas": 0,
        "estatus_semaforo": "Gris",
        "mensaje": "Sin datos suficientes para evaluar"
    }
    
    if df.empty or df.shape[0] == 0:
        return resultado

    # Normalizamos los nombres de las columnas a minúsculas
    columnas = [c.lower() for c in df.columns]
    df.columns = columnas

    # --- BUSQUEDA DE VARIABLES ---
    col_programado = next((c for c in columnas if 'programado' in c or 'meta' in c or 'prog' in c), None)
    # Buscamos la columna de resultados (atendidos, alcanzado, etc.)
    col_alcanzado = next((c for c in columnas if 'alcanzado' in c or 'realizado' in c or 'ejecutado' in c or 'atendidos' in c or 'total' in c), None)

    # Si por alguna razón tiene ambas columnas (Eficacia tradicional)
    if col_programado and col_alcanzado:
        try:
            total_prog = pd.to_numeric(df[col_programado], errors='coerce').sum()
            total_alc = pd.to_numeric(df[col_alcanzado], errors='coerce').sum()
            
            if total_prog > 0:
                porcentaje = round((total_alc / total_prog) * 100, 2)
                resultado["porcentaje_cumplimiento"] = porcentaje
                resultado["total_metas_programadas"] = int(total_prog)
                resultado["total_metas_alcanzadas"] = int(total_alc)
                
                if porcentaje >= 80.0:
                    resultado["estatus_semaforo"] = "Verde"
                    resultado["mensaje"] = "Cumplimiento Excelente conforme a las metas del PMD."
                elif porcentaje >= 70.0:
                    resultado["estatus_semaforo"] = "Amarillo"
                    resultado["mensaje"] = "Cumplimiento Aceptable. Requiere monitoreo preventivo."
                else:
                    resultado["estatus_semaforo"] = "Rojo"
                    resultado["mensaje"] = "Alerta de Subejercicio o Incumplimiento de Metas."
                return resultado
        except:
            pass

    # --- ENFOQUE OPERATIVO (ALTERNATIVA A ACTIVADA) ---
    # Si no existe columna de metas programadas, sumamos el volumen real atendido
    if col_alcanzado:
        try:
            total_gestionado = int(pd.to_numeric(df[col_alcanzado], errors='coerce').sum())
        except:
            total_gestionado = df.shape[0]
    else:
        total_gestionado = df.shape[0]

    resultado["porcentaje_cumplimiento"] = 100.0  # Representa el 100% de la actividad operativa registrada
    resultado["total_metas_programadas"] = df.shape[0] # Usamos esto para contar el número de actividades diferentes
    resultado["total_metas_alcanzadas"] = total_gestionado # Volumen bruto de personas o apoyos de la dirección
    resultado["estatus_semaforo"] = "Azul"
    resultado["mensaje"] = "Ventana operativa de gestión continua activada (Recopilación de variables de área)."
    
    return resultado
