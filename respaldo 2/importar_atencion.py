import sqlite3
import pandas as pd

def importar_csv_atencion():
    nombre_archivo = 'base de datos nueva Atencion Ciudadana.csv'
    
    try:
        # 1. Leer archivo
        df_raw = pd.read_csv(nombre_archivo, encoding='latin-1')

        # --- SECCIÓN A: CANALIZACIONES POR ÁREA ---
        # Columnas: Mes(0), Área(1), Cantidad(2)
        df_a = df_raw.iloc[:, [0, 1, 2]].copy()
        df_a.columns = ['mes', 'area_o_localidad', 'cantidad']
        df_a['actividad_tipo'] = 'CANALIZACION'
        df_a = df_a.dropna(subset=['mes', 'area_o_localidad'])

        # --- SECCIÓN B: ATENCIÓN POR LOCALIDAD ---
        # Columnas: Mes(5), Localidad(6), Cantidad(7)
        df_b = df_raw.iloc[:, [5, 6, 7]].copy()
        df_b.columns = ['mes', 'area_o_localidad', 'cantidad']
        df_b['actividad_tipo'] = 'ATENCION_LOCALIDAD'
        df_b = df_b.dropna(subset=['mes', 'area_o_localidad'])

        # Consolidar
        df_final = pd.concat([df_a, df_b], ignore_index=True)
        df_final['mes'] = df_final['mes'].str.strip().str.upper()
        df_final['cantidad'] = pd.to_numeric(df_final['cantidad'], errors='coerce').fillna(0)
        df_final['anio'] = '2026'

        # Mapa de Trimestres
        mapa_trim = {'ENERO':'1er','FEBRERO':'1er','MARZO':'1er','ABRIL':'2do','MAYO':'2do','JUNIO':'2do',
                     'JULIO':'3er','AGOSTO':'3er','SEPTIEMBRE':'3er','OCTUBRE':'4to','NOVIEMBRE':'4to','DICIEMBRE':'4to'}
        df_final['trimestre'] = df_final['mes'].map(mapa_trim) + " Trimestre"

        # 2. Cargar a SQL
        conn = sqlite3.connect('municipio.db')
        conn.execute("DELETE FROM atencion_ciudadana")
        df_final.to_sql('atencion_ciudadana', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"🚀 ¡Éxito! {len(df_final)} registros de Atención Ciudadana importados.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    importar_csv_atencion()
