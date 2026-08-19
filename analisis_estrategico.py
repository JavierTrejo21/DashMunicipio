# analisis_estrategico.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

# -----------------------------------------------------------------
# 1. IMPORTACIÓN DE LOS MÓDULOS INDEPENDIENTES POR ÁREA
# -----------------------------------------------------------------
from areas.atencion_ciudadana import analizar_atencion_ciudadana
from areas.apoyos_economicos import analizar_apoyos_economicos
from areas.bibliotecas import analizar_bibliotecas
from areas.catastro import analizar_catastro
from areas.desarrollo_social import analizar_desarrollo_social
from areas.adultos_mayores import analizar_adultos_mayores
from areas.programa_1000_dias import analizar_programa_1000_dias
from areas.dif_juridico import analizar_dif_juridico
from areas.dif_psicologia import analizar_dif_psicologia
from areas.ecologia import analizar_ecologia
from areas.grupos_vulnerables import analizar_grupos_vulnerables
from areas.estado_familiar import analizar_estado_familiar
from areas.conciliacion_municipal import analizar_conciliacion_municipal
from areas.seguridad_publica import analizar_seguridad_publica
from areas.licencias_reglamentos import analizar_licencias_reglamentos
from areas.traslados_municipales import analizar_traslados_municipales
from areas.ubr import analizar_unidad_basica_rehabilitacion
from areas.mujeres import analizar_instancia_mujeres
from areas.obras_publicas import analizar_obras_publicas
from areas.orientacion_alimentaria import analizar_orientacion_alimentaria
from areas.desayunos_escolares import analizar_desayunos_escolares
from areas.proteccion_civil import analizar_proteccion_civil
from areas.pueblos_indigenas import analizar_pueblos_indigenas
from areas.recepcion_presidenta import analizar_recepcion_presidenta
from areas.secretaria_general import analizar_secretaria_general


def analizar_datos_estrategicos(nombre_archivo, df):
    """
    Enrutador central del Dashboard.
    Recibe el identificador del archivo seleccionado y los datos cargados (DataFrame),
    aplica una limpieza global estricta para eliminar filas vacías y ejecuta el módulo.
    """

    # --- LIMPIEZA GLOBAL PROFUNDA DE DATAFRAMES (ELIMINACIÓN DE FANTASMAS) ---
    if isinstance(df, pd.DataFrame) and not df.empty:
        # 1. Elimina filas completamente vacías
        df = df.dropna(how='all')
        
        # 2. Limpieza de strings y conversión de nulos técnicos
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()
                
        # 3. Elimina filas donde las columnas principales estén vacías o contengan 'nan'
        columnas_verificacion = [c for c in df.columns if c in ['MES', 'COMUNIDAD', 'CATEGORIA', 'DESCRIPCION', 'TIPO', 'CONCEPTO']]
        if columnas_verificacion:
            # Filtra el DataFrame para retener únicamente filas que tengan contenido real en alguna de sus columnas clave
            condicion_valida = False
            for col in columnas_verificacion:
                condicion_valida = condicion_valida | (df[col] != '') & (df[col].str.lower() != 'nan')
            df = df[condicion_valida]
            
        # 4. Elimina cualquier registro residual donde no existan datos alfanuméricos
        df = df[df.astype(str).apply(lambda x: ''.join([str(v) for v in x if pd.notna(v)]).strip() != '', axis=1)]
    # ---------------------------------------------------------------------

        # Si el archivo seleccionado se encuentra en nuestro mapa de soluciones
    func_analisis = MAPEO_ANALISIS.get(nombre_archivo)

    # REFUERZO DE BÚSQUEDA: Si no hay coincidencia, normalizar agresivamente para encontrar en el mapeo
    if func_analisis is None and isinstance(nombre_archivo, str):
        import unicodedata
        import re
        def norm_key(s):
            # Quitar acentos, reemplazar no-alfanuméricos por _, colapsar _ y pasar a Mayúsculas
            s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            s = re.sub(r'[^a-zA-Z0-9]', '_', s).upper()
            return re.sub(r'_+', '_', s).strip('_')
        
        nombre_norm = norm_key(nombre_archivo)
        func_analisis = MAPEO_ANALISIS.get(nombre_norm)
        
        # Reintento con normalización simple por si acaso
        if func_analisis is None:
            nombre_simple = " ".join(nombre_archivo.replace("·", " ").split())
            func_analisis = MAPEO_ANALISIS.get(nombre_simple)

    if func_analisis is not None:
        try:
            # Ejecuta la función específica devolviendo el layout envuelto con la colorimetría estructurada (#781d37, #920d24, #1ca2a9)
            contenido_grafico = func_analisis(df)
            return html.Div(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [contenido_grafico],
                                className="p-4",
                            )
                        ],
                        className="shadow-sm border-0 rounded-4 bg-white mb-4",
                        style={
                            "borderTop": "4px solid #781d37 !important"
                        }
                    )
                ]
            )
        except Exception as e:
            # Control de errores robusto estilizado
            return dbc.Alert(
                [
                    html.Div(
                        [
                            html.I(
                                className="bi bi-exclamation-octagon-fill me-2 fs-5"
                            ),
                            html.Strong(
                                f"Error en el módulo '{nombre_archivo}': "
                            ),
                            html.Span(str(e)),
                        ],
                        className="d-flex align-items-center",
                    )
                ],
                color="danger",
                className="m-3 shadow-sm border-0 rounded-3",
            )

    # Si el usuario selecciona un área que aún no tiene módulo analítico
    return dbc.Alert(
        [
            html.Div(
                [
                    html.I(className="bi bi-info-circle-fill me-2 fs-5", style={"color": "#1ca2a9"}),
                    html.Span(
                        f"El área '{nombre_archivo}' está registrada correctamente, pero aún no se ha configurado su tablero de análisis estratégico personalizado.",
                        style={"color": "#1f2937"}
                    ),
                ],
                className="d-flex align-items-center",
            )
        ],
        className="m-3 shadow-sm border-0 rounded-3 text-dark bg-light",
        style={"borderLeft": "4px solid #1ca2a9"}
    )


# -----------------------------------------------------------------
# 3. DICCIONARIO CENTRALIZADO DE ENRUTAMIENTO (MAPEO)
# -----------------------------------------------------------------
MAPEO_ANALISIS = {
    # --- ÁREA: RECEPCIÓN DE LA PRESIDENTA ---
    "2_1_RECEPCION_MUNICIPAL_PRESIDENTA": analizar_recepcion_presidenta,
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
    "4_1_ECOLOGIA_Y_MEDIO_AMBIENTE": analizar_ecologia,
    "ECOLOGIA_Y_MEDIO_AMBIENTE": analizar_ecologia,
    "ecologia": analizar_ecologia,
    # --- ÁREA: 2.12 UNIDAD BÁSICA DE REHABILITACIÓN (UBR) ---
    "2.12 UNIDAD BÁSICA DE REHABILITACIÓN - UBR.xlsx - Hoja1.csv": analizar_unidad_basica_rehabilitacion,
    "2.12 UNIDAD BÁSICA DE REHABILITACIÓN - UBR.xlsx - Hoja1": analizar_unidad_basica_rehabilitacion,
    "2.12 UNIDAD BÁSICA DE REHABILITACIÓN - UBR": analizar_unidad_basica_rehabilitacion,
    "2.12 UNIDAD BASICA DE REHABILITACION - UBR.xlsx - Hoja1.csv": analizar_unidad_basica_rehabilitacion,
    "2.12 UNIDAD BASICA DE REHABILITACION - UBR.xlsx - Hoja1": analizar_unidad_basica_rehabilitacion,
    "2.12 UNIDAD BASICA DE REHABILITACION - UBR": analizar_unidad_basica_rehabilitacion,
    "2_12_UNIDAD_BASICA_DE_REHABILITACION_UBR": analizar_unidad_basica_rehabilitacion,
    "UNIDAD_BASICA_DE_REHABILITACION_UBR": analizar_unidad_basica_rehabilitacion,
    "ubr": analizar_unidad_basica_rehabilitacion,
    # --- ÁREA: 2.1.4 DIF DESAYUNOS ESCOLARES ---
    "2_1_4_DIF_DESAYUNOS_ESCOLARES": analizar_desayunos_escolares,
    "2.1.4 DIF DESAYUNOS ESCOLARES": analizar_desayunos_escolares,
    "2.1.4 DIF DESAYUNOS ESCOLARES.xlsx": analizar_desayunos_escolares,
    "2.1.4 DIF DESAYUNOS ESCOLARES.xlsx - Hoja1": analizar_desayunos_escolares,
    "2.1.4 DIF DESAYUNOS ESCOLARES.xlsx - Hoja1.csv": analizar_desayunos_escolares,
    "DIF_DESAYUNOS_ESCOLARES": analizar_desayunos_escolares,
    "desayunos_escolares": analizar_desayunos_escolares,
    # --- ÁREA: 2.11 TRASLADOS MUNICIPALES ---
    "2.11 TRASLADOS MUNICIPALES.xlsx - Hoja1.csv": analizar_traslados_municipales,
    "2.11 TRASLADOS MUNICIPALES.xlsx - Hoja1": analizar_traslados_municipales,
    "2.11 TRASLADOS MUNICIPALES": analizar_traslados_municipales,
    "2.11 TRASLADOS DIF.xlsx - Hoja1.csv": analizar_traslados_municipales,
    "2.11 TRASLADOS DIF.xlsx - Hoja1": analizar_traslados_municipales,
    "2.11 TRASLADOS DIF": analizar_traslados_municipales,
    "2_11_TRASLADOS_MUNICIPALES": analizar_traslados_municipales,
    "TRASLADOS_MUNICIPALES": analizar_traslados_municipales,
    "traslados": analizar_traslados_municipales,
    # --- ÁREA: 2.1.2 DIF APOYOS ECONÓMICOS ---
    "2_1_2_DIF_APOYOS_ECONOMICOS": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONOMICOS": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONÓMICOS": analizar_apoyos_economicos,
    "DIF_APOYOS_ECONOMICOS": analizar_apoyos_economicos,
    "APOYOS_ECONOMICOS": analizar_apoyos_economicos,
    "apoyos_economicos": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONOMICOS.xlsx": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONÓMICOS.xlsx": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONOMICOS.xlsx - Hoja1": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONÓMICOS.xlsx - Hoja1": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONOMICOS.xlsx - Hoja1.csv": analizar_apoyos_economicos,
    "2.1.2 DIF APOYOS ECONOMICOS.xlsx - Hoja1.csv": analizar_apoyos_economicos,
    # --- ÁREA: 1.4 PUEBLOS INDÍGENAS ---
    "1.4 PUEBLOS INDIGENAS": analizar_pueblos_indigenas,
    "1_4_PUEBLOS_INDIGENAS": analizar_pueblos_indigenas,
    "PUEBLOS_INDIGENAS": analizar_pueblos_indigenas,
    "1.4 PUEBLOS INDIGENAS.xlsx - Hoja1": analizar_pueblos_indigenas,
    "1_4_PUEBLOS_INDIGENAS_XLSX___HOJA1": analizar_pueblos_indigenas,
    (
        "1.4 PUEBLOS INDIGENAS.xlsx - base de datos nueva lenguas ind"
    ): analizar_pueblos_indigenas,
    (
        "1_4_PUEBLOS_INDIGENAS_XLSX___BASE_DE_DATOS_NUEVA_LENGUAS_IND"
    ): analizar_pueblos_indigenas,
    "BASE_DE_DATOS_NUEVA_LENGUAS_IND": analizar_pueblos_indigenas,
    # --- ÁREA: 2.1.3 DIF APOYOS ATENCIÓN A ADULTOS MAYORES ---
    "2_1_3_DIF_APOYOS_ATENCION_A_ADULTOS_MAYORES": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCION A ADULTOS MAYORES": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCIÓN A ADULTOS MAYORES": analizar_adultos_mayores,
    "ADULTOS_MAYORES": analizar_adultos_mayores,
    "adultos_mayores": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCION A ADULTOS MAYORES.xlsx": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCIÓN A ADULTOS MAYORES.xlsx": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCION A ADULTOS MAYORES.xlsx - Hoja1": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCIÓN A ADULTOS MAYORES.xlsx - Hoja1": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCION A ADULTOS MAYORES.xlsx - Hoja1.csv": analizar_adultos_mayores,
    "2.1.3 DIF APOYOS ATENCIÓN A ADULTOS MAYORES.xlsx - Hoja1.csv": analizar_adultos_mayores,
    # --- ÁREA: 2.1.6 DIF PROGRAMA 1000 DÍAS ---
    "2_1_6_DIF_PROGRAMA_1000_DIAS": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DIAS": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DÍAS": analizar_programa_1000_dias,
    "PROGRAMA_1000_DIAS": analizar_programa_1000_dias,
    "programa_1000_dias": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DIAS.xlsx": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DÍAS.xlsx": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DIAS.xlsx - Hoja1": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DÍAS.xlsx - Hoja1": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DIAS.xlsx - Hoja1.csv": analizar_programa_1000_dias,
    "2.1.6 DIF PROGRAMA 1000 DÍAS.xlsx - Hoja1.csv": analizar_programa_1000_dias,
    # --- ÁREA: 2.2.5 DIF JURÍDICO ---
    "2_2_5_DIF_JURIDICO": analizar_dif_juridico,
    "2.2.5 DIF JURIDICO": analizar_dif_juridico,
    "2.2.5 DIF JURÍDICO": analizar_dif_juridico,
    "DIF_JURIDICO": analizar_dif_juridico,
    "dif_juridico": analizar_dif_juridico,
    "2.2.5 DIF JURIDICO.xlsx": analizar_dif_juridico,
    "2.2.5 DIF JURÍDICO.xlsx": analizar_dif_juridico,
    "2.2.5 DIF JURIDICO.xlsx - Hoja1": analizar_dif_juridico,
    "2.2.5 DIF JURÍDICO.xlsx - Hoja1": analizar_dif_juridico,
    "2.2.5 DIF JURIDICO.xlsx - Hoja1.csv": analizar_dif_juridico,
    "2.2.5 DIF JURÍDICO.xlsx - Hoja1.csv": analizar_dif_juridico,
    # --- ÁREA: 1.7 REGISTRO DEL ESTADO FAMILIAR ---
    "1_7_REGISTRO_DEL_ESTADO_FAMILIAR": analizar_estado_familiar,
    "1.7 REGISTRO DEL ESTADO FAMILIAR": analizar_estado_familiar,
    "REGISTRO_DEL_ESTADO_FAMILIAR": analizar_estado_familiar,
    "estado_familiar": analizar_estado_familiar,
    "1.7 REGISTRO DEL ESTADO FAMILIAR.xlsx": analizar_estado_familiar,
    "1.7 REGISTRO DEL ESTADO FAMILIAR.xlsx - Hoja1": analizar_estado_familiar,
    "1.7 REGISTRO DEL ESTADO FAMILIAR.xlsx - Hoja1.csv": analizar_estado_familiar,
    # --- ÁREA: 1.2 CONCILIACIÓN MUNICIPAL ---
    "1_2_CONCILIACION_MUNICIPAL": analizar_conciliacion_municipal,
    "1.2 CONCILIACION MUNICIPAL": analizar_conciliacion_municipal,
    "1.2 CONCILIACIÓN MUNICIPAL": analizar_conciliacion_municipal,
    "CONCILIACION_MUNICIPAL": analizar_conciliacion_municipal,
    "conciliacion_municipal": analizar_conciliacion_municipal,
    "1.2 CONCILIACION MUNICIPAL.xlsx": analizar_conciliacion_municipal,
    "1.2 CONCILIACIÓN MUNICIPAL.xlsx": analizar_conciliacion_municipal,
    "1.2 CONCILIACION MUNICIPAL.xlsx - Hoja1": analizar_conciliacion_municipal,
    "1.2 CONCILIACIÓN MUNICIPAL.xlsx - Hoja1": analizar_conciliacion_municipal,
    "1.2 CONCILIACION MUNICIPAL.xlsx - Hoja1.csv": analizar_conciliacion_municipal,
    "1.2 CONCILIACIÓN MUNICIPAL.xlsx - Hoja1.csv": analizar_conciliacion_municipal, 
    # --- ÁREA: 1.1 SEGURIDAD PÚBLICA ---
    "1_1_SEGURIDAD_PUBLICA": analizar_seguridad_publica,
    "1.1 SEGURIDAD PUBLICA": analizar_seguridad_publica,
    "1.1 SEGURIDAD PÚBLICA": analizar_seguridad_publica,
    "SEGURIDAD_PUBLICA": analizar_seguridad_publica,
    "seguridad_publica": analizar_seguridad_publica,
    "1.1 SEGURIDAD PUBLICA.xlsx": analizar_seguridad_publica,
    "1.1 SEGURIDAD PÚBLICA.xlsx": analizar_seguridad_publica,
    "1.1 SEGURIDAD PUBLICA.xlsx - Hoja1": analizar_seguridad_publica,
    "1.1 SEGURIDAD PÚBLICA.xlsx - Hoja1": analizar_seguridad_publica,
    "1.1 SEGURIDAD PUBLICA.xlsx - Hoja1.csv": analizar_seguridad_publica,
    "1.1 SEGURIDAD PÚBLICA.xlsx - Hoja1.csv": analizar_seguridad_publica,
    # --- ÁREA: 5.1 DESARROLLO SOCIAL ---
    "5.1 DESARROLLO SOCIAL": analizar_desarrollo_social,
    "5_1_DESARROLLO_SOCIAL": analizar_desarrollo_social,
    "DESARROLLO_SOCIAL": analizar_desarrollo_social,
    "5.1 DESARROLLO SOCIAL.xlsx - Hoja1": analizar_desarrollo_social,
    "5_1_DESARROLLO_SOCIAL_XLSX___HOJA1": analizar_desarrollo_social,
    # --- ÁREA: 5.3 INSTANCIA DE LAS MUJERES ---
    (
        "2.3 INSTANCIA MUNICIPAL PARA EL DESARROLLO DE LAS MUJERES"
    ): analizar_instancia_mujeres,
    (
        "2.3 INSTANCIA MUNICIPAL PARA EL DESARROLLO DE LAS MUJERES.xlsx -"
        " Hoja1"
    ): analizar_instancia_mujeres,
    (
        "2_3_INSTANCIA_MUNICIPAL_PARA_EL_DESARROLLO_DE_LAS_MUJERES"
    ): analizar_instancia_mujeres,
    "INSTANCIA  _MUJERES": analizar_instancia_mujeres,
    # --- ÁREA: 5.4 ATENCIÓN CIUDADANA ---
    "5.4 ATENCIÓN CIUDADANA": analizar_atencion_ciudadana,
    "5.4 ATENCION CIUDADANA": analizar_atencion_ciudadana,
    "5_4_ATENCION_CIUDADANA": analizar_atencion_ciudadana,
    "ATENCION_CIUDADANA": analizar_atencion_ciudadana,
    "5.4 ATENCIÓN CIUDADANA.xlsx - Hoja1": analizar_atencion_ciudadana,
    "5.4 ATENCIÓN CIUDADANA.xlsx - Hoja1.csv": analizar_atencion_ciudadana,
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
    "3.2 · LICENCIAS Y REGLAMENTOS": analizar_licencias_reglamentos,
    "3.2 LICENCIAS Y REGLAMENTOS.xlsx - Hoja1": analizar_licencias_reglamentos,
    "3.2 LICENCIAS Y REGLAMENTOS.xlsx - Hoja1.csv": (
        analizar_licencias_reglamentos
    ),
    # --- ÁREA: 3.5 BIBLIOTECAS Y C.C.A. ---
    "3_5_BIBLIOTECAS_Y_C_C_A": analizar_bibliotecas,
    "BIBLIOTECAS_C_C_A": analizar_bibliotecas,
    "3.5 BIBLIOTECAS y C.C.A.": analizar_bibliotecas,
    "3.5 BIBLIOTECAS Y C.C.A": analizar_bibliotecas,
    "3.5 BIBLIOTECAS Y C.C.A.": analizar_bibliotecas,
    "3.5 BIBLIOTECAS y C.C.A.xlsx - Hoja1": analizar_bibliotecas,
    "3.5 BIBLIOTECAS y C.C.A.xlsx - Hoja1.csv": analizar_bibliotecas,
    # --- ÁREA: 1.5 SECRETARÍA GENERAL ---
    "1_5_SECRETARIA_GENERAL": analizar_secretaria_general,
    "SECRETARIA_GENERAL": analizar_secretaria_general,
    "1.5 SECRETARIA GENERAL": analizar_secretaria_general,
    "1.5 SECRETARIA GENERAL.xlsx - Hoja1": analizar_secretaria_general,
    "1.5 SECRETARIA GENERAL.xlsx - Hoja1.csv": analizar_secretaria_general,
    # --- ÁREA: 2.6 DIF PSICOLOGÍA ---
    "2_6_DIF_PSICOLOGIA": analizar_dif_psicologia,
    "DIF_PSICOLOGIA": analizar_dif_psicologia,
    "2.6 DIF PSICOLOGIA": analizar_dif_psicologia,
    "2.6 DIF PSICOLOGIA.xlsx - Hoja1": analizar_dif_psicologia,
    "2.6 DIF PSICOLOGIA.xlsx - Hoja1.csv": analizar_dif_psicologia,
    # --- ÁREA: 2.2.8 GRUPOS VULNERABLES ---
    (
        "2_2_8_DIF_PROGRAMAS_INTEGRALES_DE_ATENCION_A_GRUPOS_VULNERABLES"
    ): analizar_grupos_vulnerables,
    "GRUPOS_VULNERABLES": analizar_grupos_vulnerables,
    (
        "2.2.8 DIF PROGRAMAS INTEGRALES DE ATENCIÓN A GRUPOS VULNERABLES"
    ): analizar_grupos_vulnerables,
    (
        "2.2.8 DIF PROGRAMAS INTEGRALES DE ATENCIÓN A GRUPOS VULNERABLES.xlsx -"
        " Hoja1"
    ): analizar_grupos_vulnerables,
    (
        "2.2.8 DIF PROGRAMAS INTEGRALES DE ATENCIÓN A GRUPOS VULNERABLES.xlsx -"
        " Hoja1.csv"
    ): analizar_grupos_vulnerables,
    # --- ÁREA: 2.2.7 ORIENTACIÓN Y EDUCACIÓN ALIMENTARIA ---
    (
        "2_2_7_DIF_PROGRAMAS_DE_ORIENTACION_Y_EDUCACION_ALIMENTARIA"
    ): analizar_orientacion_alimentaria,
    "ORIENTACION_ALIMENTARIA": analizar_orientacion_alimentaria,
    (
        "2.2.7 DIF PROGRAMAS DE ORIENTACION Y EDUCACION ALIMENTARIA"
    ): analizar_orientacion_alimentaria,
    (
        "2.2.7 DIF PROGRAMAS DE ORIENTACION Y EDUCACION ALIMENTARIA.xlsx -"
        " Hoja2.csv"
    ): analizar_orientacion_alimentaria,
}