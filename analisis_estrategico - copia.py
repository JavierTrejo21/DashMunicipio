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
from areas.atencion_ciudadana import analizar_atencion_ciudadana
from areas.ecologia import analizar_ecologia
from areas.catastro import analizar_catastro
from areas.proteccion_civil import analizar_proteccion_civil
from areas.licencias_reglamentos import analizar_licencias_reglamentos
from areas.bibliotecas import analizar_bibliotecas
from areas.secretaria_general import analizar_secretaria_general
from areas.dif_psicologia import analizar_dif_psicologia
from areas.grupos_vulnerables import analizar_grupos_vulnerables
from areas.orientacion_alimentaria import analizar_orientacion_alimentaria

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

    # --- ÁREA: 4.1 ECOLOGÍA Y MEDIO AMBIENTE ---
    "4.1 ECOLOGIA Y MEDIO AMBIENTE.xlsx - Hoja1.csv": analizar_ecologia,
    "4.1 ECOLOGIA Y MEDIO AMBIENTE.xlsx - Hoja1": analizar_ecologia,
    "4.1 ECOLOGIA Y MEDIO AMBIENTE": analizar_ecologia,
    "4.1 ECOLOGÍA Y MEDIO AMBIENTE.xlsx - Hoja1.csv": analizar_ecologia,
    "4.1 ECOLOGÍA Y MEDIO AMBIENTE.xlsx - Hoja1": analizar_ecologia,
    "4.1 ECOLOGÍA Y MEDIO AMBIENTE": analizar_ecologia,
    
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
    "INSTANCIA_MUJERES": analizar_instancia_mujeres,

    # --- ÁREA: 5.4 ATENCIÓN CIUDADANA ---
    "5.4 ATENCIÓN CIUDADANA": analizar_atencion_ciudadana,
    "5.4 ATENCION CIUDADANA": analizar_atencion_ciudadana,
    "5_4_ATENCION_CIUDADANA": analizar_atencion_ciudadana,
    "ATENCION_CIUDADANA": analizar_atencion_ciudadana,
    "5.4 ATENCIÓN CIUDADANA.xlsx - Hoja1": analizar_atencion_ciudadana,
    "5.4 ATENCIÓN CIUDADANA.xlsx - Hoja1.csv": analizar_atencion_ciudadana,

    # --- ÁREA: 4.1 ECOLOGÍA Y MEDIO AMBIENTE ---
    "4.1 ECOLOGÍA Y MEDIO AMBIENTE": analizar_ecologia,
    "4.1 ECOLOGIA Y MEDIO AMBIENTE": analizar_ecologia,
    "4_1_ECOLOGIA_Y_MEDIO_AMBIENTE": analizar_ecologia,
    "ECOLOGIA_Y_MEDIO_AMBIENTE": analizar_ecologia,
    "4.1 ECOLOGÍA Y MEDIO AMBIENTE.xlsx - Hoja1": analizar_ecologia,
    "4.1 ECOLOGÍA Y MEDIO AMBIENTE.xlsx - Hoja1.csv": analizar_ecologia,
    
    # --- ÁREA: 4.4 CATASTRO MUNICIPAL ---
    "4_4_CATASTRO_MUNICIPAL": analizar_catastro,
    "CATASTRO_MUNICIPAL": analizar_catastro,
    "4.4 CATASTRO MUNICIPAL": analizar_catastro,
    "4.4 CATASTRO MUNICIPAL.xlsx - Hoja1": analizar_catastro,
    "4.4 CATASTRO MUNICIPAL.xlsx - Hoja1.csv": analizar_catastro,

    # --- ÁREA: 4.2 PROTECCIÓN CIVIL ---
    "4_2_PROTECCION_CIVIL": analizar_proteccion_civil,
    "PROTECTOR_CIVIL": analizar_proteccion_civil,
    "4.2 PROTECCIÓN CIVIL": analizar_proteccion_civil,
    "4.2 PROTECCIÓN CIVIL.xlsx - Hoja1": analizar_proteccion_civil,
    "4.2 PROTECCIÓN CIVIL.xlsx - Hoja1.csv": analizar_proteccion_civil,

    # --- ÁREA: 3.2 LICENCIAS Y REGLAMENTOS ---
    "3_2_LICENCIAS_Y_REGLAMENTOS": analizar_licencias_reglamentos,
    "LICENCIAS_Y_REGLAMENTOS": analizar_licencias_reglamentos,
    "3.2 LICENCIAS Y REGLAMENTOS": analizar_licencias_reglamentos,
    "3.2 LICENCIAS Y REGLAMENTOS.xlsx - Hoja1": analizar_licencias_reglamentos,
    "3.2 LICENCIAS Y REGLAMENTOS.xlsx - Hoja1.csv": analizar_licencias_reglamentos,

    # --- ÁREA: 3.5 BIBLIOTECAS Y C.C.A. ---
    "3_5_BIBLIOTECAS_Y_C_C_A": analizar_bibliotecas,
    "BIBLIOTECAS_C_C_A": analizar_bibliotecas,
    "3.5 BIBLIOTECAS y C.C.A.": analizar_bibliotecas,
    "3.5 BIBLIOTECAS y C.C.A.xlsx - Hoja1": analizar_bibliotecas,
    "3.5 BIBLIOTECAS y C.C.A.xlsx - Hoja1.csv": analizar_bibliotecas,

    # --- ÁREA: 2.10 SECRETARÍA GENERAL ---  👈 ¡PEGA ESTE BLOQUE COMPLETO AQUÍ!
    "2_10_SECRETARIA_GENERAL": analizar_secretaria_general,
    "SECRETARIA_GENERAL": analizar_secretaria_general,
    "2.10 SECRETARIA GENERAL": analizar_secretaria_general,
    "2.10 SECRETARIA GENERAL.xlsx - Hoja1": analizar_secretaria_general,
    "2.10 SECRETARIA GENERAL.xlsx - Hoja1.csv": analizar_secretaria_general,

    # --- ÁREA: 2.6 DIF PSICOLOGÍA ---
    "2_6_DIF_PSICOLOGIA": analizar_dif_psicologia,
    "DIF_PSICOLOGIA": analizar_dif_psicologia,
    "2.6 DIF PSICOLOGIA": analizar_dif_psicologia,
    "2.6 DIF PSICOLOGIA.xlsx - Hoja1": analizar_dif_psicologia,
    "2.6 DIF PSICOLOGIA.xlsx - Hoja1.csv": analizar_dif_psicologia,

    # --- ÁREA: 2.2.8 GRUPOS VULNERABLES ---
    "2_2_8_DIF_PROGRAMAS_INTEGRALES_DE_ATENCION_A_GRUPOS_VULNERABLES": analizar_grupos_vulnerables,
    "GRUPOS_VULNERABLES": analizar_grupos_vulnerables,
    "2.2.8 DIF PROGRAMAS INTEGRALES DE ATENCIÓN A GRUPOS VULNERABLES": analizar_grupos_vulnerables,
    "2.2.8 DIF PROGRAMAS INTEGRALES DE ATENCIÓN A GRUPOS VULNERABLES.xlsx - Hoja1": analizar_grupos_vulnerables,
    "2.2.8 DIF PROGRAMAS INTEGRALES DE ATENCIÓN A GRUPOS VULNERABLES.xlsx - Hoja1.csv": analizar_grupos_vulnerables,

    # --- ÁREA: 2.2.7 DIF_PROGRAMAS_DE_ORIENTACION_Y_EDUCACION_ALIMENTARIA ---
    "2_2_7_DIF_PROGRAMAS_DE_ORIENTACION_Y_EDUCACION_ALIMENTARIA": analizar_orientacion_alimentaria,
    "ORIENTACION_ALIMENTARIA": analizar_orientacion_alimentaria,
    "2.2.7 DIF PROGRAMAS DE ORIENTACION Y EDUCACION ALIMENTARIA": analizar_orientacion_alimentaria,
    "2.2.7 DIF PROGRAMAS DE ORIENTACION Y EDUCACION ALIMENTARIA.xlsx - Hoja2.csv": analizar_orientacion_alimentaria,
    }
