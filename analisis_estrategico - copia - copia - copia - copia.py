# analisis_estrategico.py
import dash_bootstrap_components as dbc

# -----------------------------------------------------------------
# 1. IMPORTACIÓN DE LOS MÓDULOS INDEPENDIENTES POR ÁREA
# -----------------------------------------------------------------
# Cada área administrativa vive en su propio archivo dentro de la carpeta 'areas'
from areas.recepcion_presidenta import analizar_recepcion_presidenta
from areas.obras_publicas import analizar_obras_publicas
from areas.pueblos_indigenas import analizar_pueblos_indigenas
from areas.desarrollo_social import analizar_desarrollo_social  
from areas.mujeres import analizar_instancia_mujeres  # <-- NUEVA IMPORTACIÓN CONECTADA


def analizar_datos_estrategicos(nombre_archivo, df):
    """
    Enrutador central del Dashboard.
    Recibe el identificador del archivo seleccionado y los datos cargados (DataFrame),
    busca la función analítica correspondiente en el MAPEO y la ejecuta bajo demanda.
    """
    
    # Si el archivo seleccionado se encuentra en nuestro mapa de soluciones
    if nombre_archivo in MAPEO_ANALISIS:
        func_analisis = MAPEO_ANALISIS[nombre_archivo]
        try:
            # Ejecuta la función específica de la sección pasando el DataFrame
            return func_analisis(df)
        except Exception as e:
            # Control de errores robusto para evitar que la app completa se caiga
            return dbc.Alert(
                f"⚠️ Error crítico al renderizar el módulo '{nombre_archivo}': {str(e)}", 
                color="danger", 
                className="m-3 shadow-sm"
            )
            
    # Si el usuario sube un archivo que aún no ha sido programado
    return dbc.Alert(
        f"📊 El archivo '{nombre_archivo}' se cargó con éxito, pero aún no se ha configurado un módulo de análisis estratégico para esta área administrativa.",
        color="info",
        className="m-3 shadow-sm"
    )


# -----------------------------------------------------------------
# 3. DICCIONARIO CENTRALIZADO DE ENRUTAMIENTO (MAPEO)
# -----------------------------------------------------------------
MAPEO_ANALISIS = {
    # --- ÁREA: RECEPCIÓN DE LA PRESIDENTA ---
    "5_1_1_RECEPCION_MUNICIPAL_PRESIDENTA": analizar_recepcion_presidenta,
    "RECEPCION_MUNICIPAL_PRESIDENTA": analizar_recepcion_presidenta,
    
    # --- ÁREA: OBRAS PÚBLICAS ---
    "4_5_OBRAS_PUBLICAS": analizar_obras_publicas,
    "OBRAS_PUBLICAS": analizar_obras_publicas,
    "4.5 OBRAS PUBLICAS": analizar_obras_publicas,
    "4.5 OBRAS PUBLICAS.xlsx - Hoja1": analizar_obras_publicas,
    
    # --- ÁREA: 5.1.2 PUEBLOS INDÍGENAS ---
    "5.1.2 PUEBLOS INDIGENAS": analizar_pueblos_indigenas,
    "5_1_2_PUEBLOS_INDIGENAS": analizar_pueblos_indigenas,
    "PUEBLOS_INDIGENAS": analizar_pueblos_indigenas,
    "5.1.2 PUEBLOS INDIGENAS.xlsx - Hoja1": analizar_pueblos_indigenas,
    "5_1_2_PUEBLOS_INDIGENAS_XLSX___HOJA1": analizar_pueblos_indigenas,
    "5.1.2 PUEBLOS INDIGENAS.xlsx - base de datos nueva lenguas ind": analizar_pueblos_indigenas,
    "5_1_2_PUEBLOS_INDIGENAS_XLSX___BASE_DE_DATOS_NUEVA_LENGUAS_IND": analizar_pueblos_indigenas,
    "BASE_DE_DATOS_NUEVA_LENGUAS_IND": analizar_pueblos_indigenas,

    # --- ÁREA: 5.1 DESARROLLO SOCIAL ---
    "5.1 DESARROLLO SOCIAL": analizar_desarrollo_social,
    "5_1_DESARROLLO_SOCIAL": analizar_desarrollo_social,
    "DESARROLLO_SOCIAL": analizar_desarrollo_social,
    "5.1 DESARROLLO SOCIAL.xlsx - Hoja1": analizar_desarrollo_social,
    "5_1_DESARROLLO_SOCIAL_XLSX___HOJA1": analizar_desarrollo_social,

    # --- ÁREA: 5.3 INSTANCIA DE LAS MUJERES ---
    "5.3 INSTANCIA MUNICIPAL PARA EL DESARROLLO DE LAS MUJERES": analizar_instancia_mujeres,
    "5.3 INSTANCIA MUNICIPAL PARA EL DESARROLLO DE LAS MUJERES.xlsx - Hoja1": analizar_instancia_mujeres,
    "5_3_INSTANCIA_MUNICIPAL_PARA_EL_DESARROLLO_DE_LAS_MUJERES": analizar_instancia_mujeres,
    "INSTANCIA_MUJERES": analizar_instancia_mujeres
}
