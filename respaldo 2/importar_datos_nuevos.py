import sqlite3
import pandas as pd

def importar_csv_a_juridico():
    nombre_archivo = 'base de datos nueva Unidad Juridica.csv'
    
    try:
        # Cargamos con latin-1 para los acentos
        df = pd.read_csv(nombre_archivo, encoding='latin-1')
        
        # Seleccionamos las primeras 17 columnas de datos reales
        df_principal = df.iloc[:, 0:17].copy()
        
        # Renombramos columnas para que coincidan con la base de datos SQL
        df_principal.columns = [
            'mes', 'localidad', 'descripcion', 'asesoria_tenencia', 'asesoria_civil_familiar',
            'juicios_obras', 'canalizaciones_pension', 'correcciones_actas', 'convenios_contratos',
            'audiencias_conciliador', 'visitaduria_agraria', 'catastro_deslindes', 'actas_registro_civil',
            'revision_padron', 'traslados_dominio', 'revision_avaluos', 'deslindes_area'
        ]

        # CORRECCIÓN AQUÍ: Usamos .str para procesar la columna de texto
        df_principal['mes'] = df_principal['mes'].str.strip().str.upper()

        # Convertir columnas numéricas y rellenar vacíos con 0
        cols_numericas = df_principal.columns[3:]
        for col in cols_numericas:
            df_principal[col] = pd.to_numeric(df_principal[col], errors='coerce').fillna(0)
        
        # Agregar columnas de control
        df_principal['anio'] = '2026'
        
        # Mapa de trimestres (usando el texto ya en mayúsculas)
        mapa_trim = {
            'ENERO': '1er Trimestre', 'FEBRERO': '1er Trimestre', 'MARZO': '1er Trimestre',
            'ABRIL': '2do Trimestre', 'MAYO': '2do Trimestre', 'JUNIO': '2do Trimestre',
            'JULIO': '3er Trimestre', 'AGOSTO': '3er Trimestre', 'SEPTIEMBRE': '3er Trimestre',
            'OCTUBRE': '4to Trimestre', 'NOVIEMBRE': '4to Trimestre', 'DICIEMBRE': '4to Trimestre'
        }
        df_principal['trimestre'] = df_principal['mes'].map(mapa_trim)

        # Conectar a la base de datos municipio.db
        conn = sqlite3.connect('municipio.db')
        # Limpiamos datos previos antes de importar para no duplicar
        conn.execute("DELETE FROM juridico") 
        
        # Insertar los nuevos datos
        df_principal.to_sql('juridico', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"🚀 ¡Éxito! Se importaron {len(df_principal)} registros correctamente.")
        
    except Exception as e:
        print(f"❌ Error al importar: {e}")

if __name__ == '__main__':
    importar_csv_a_juridico()
