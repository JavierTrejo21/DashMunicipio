import sqlite3
import pandas as pd
import numpy as np

def preparar_base_de_datos():
    """Crea la tabla comude si no existe."""
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS comude")
    cursor.execute('''
        CREATE TABLE comude (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            comunidad_sede TEXT,
            actividad TEXT,
            categoria TEXT,
            genero TEXT,
            cantidad_equipos INTEGER,
            participantes INTEGER,
            inversion REAL,
            lugar_especifico TEXT,
            observaciones TEXT,
            tipo_registro TEXT,
            anio TEXT,
            trimestre TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Tabla 'comude' preparada en la base de datos.")

def importar_csv_comude():
    nombre_archivo = 'base de datos nueva COMUDE.csv'
    
    try:
        # Asegurarnos de que la tabla exista antes de seguir
        preparar_base_de_datos()

        # 1. Leer el archivo completo
        df_raw = pd.read_csv(nombre_archivo, encoding='latin-1')

        # --- SECCIÓN A: TORNEOS EN COMUNIDADES ---
        df_a = df_raw.iloc[:, [0, 1, 3, 4]].copy()
        df_a.columns = ['mes', 'comunidad_sede', 'actividad', 'inversion']
        df_a['tipo_registro'] = 'TORNEO COMUNITARIO'
        df_a = df_a.dropna(subset=['mes', 'actividad'])

        # --- SECCIÓN B: TORNEOS CONTINUOS ---
        df_b = df_raw.iloc[:, [7, 8, 9, 10, 11, 12, 13]].copy()
        df_b.columns = ['mes', 'actividad', 'categoria', 'cantidad_equipos', 'inversion', 'comunidad_sede', 'observaciones']
        df_b['tipo_registro'] = 'TORNEO CONTINUO'
        df_b = df_b.dropna(subset=['mes', 'actividad'])

        # --- SECCIÓN C: DISCIPLINAS OFERTADAS ---
        df_c = df_raw.iloc[:, [0, 19, 20, 21, 22]].copy()
        df_c.columns = ['mes', 'actividad', 'categoria', 'genero', 'participantes']
        df_c['tipo_registro'] = 'DISCIPLINA'
        df_c = df_c.dropna(subset=['actividad', 'participantes'])

        # --- CONSOLIDACIÓN ---
        df_final = pd.concat([df_a, df_b, df_c], ignore_index=True)

        # Limpieza de datos
        df_final['mes'] = df_final['mes'].str.strip().str.upper()
        df_final['anio'] = '2026'
        
        # Llenado de ceros para valores numéricos
        cols_num = ['cantidad_equipos', 'participantes', 'inversion']
        for col in cols_num:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

        # Asignación de Trimestre
        mapa_trim = {
            'ENERO': '1er Trimestre', 'FEBRERO': '1er Trimestre', 'MARZO': '1er Trimestre',
            'ABRIL': '2do Trimestre', 'MAYO': '2do Trimestre', 'JUNIO': '2do Trimestre',
            'JULIO': '3er Trimestre', 'AGOSTO': '3er Trimestre', 'SEPTIEMBRE': '3er Trimestre',
            'OCTUBRE': '4to Trimestre', 'NOVIEMBRE': '4to Trimestre', 'DICIEMBRE': '4to Trimestre'
        }
        df_final['trimestre'] = df_final['mes'].map(mapa_trim).fillna('Por definir')

        # 2. Cargar a la base de datos
        conn = sqlite3.connect('municipio.db')
        df_final.to_sql('comude', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"🚀 ¡Éxito! Se procesaron y subieron {len(df_final)} registros de COMUDE.")
        
    except Exception as e:
        print(f"❌ Error al procesar COMUDE: {e}")

if __name__ == '__main__':
    importar_csv_comude()
