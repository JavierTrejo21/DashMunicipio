import sqlite3
import pandas as pd
import os
import glob

def reparar_definitivo():
    try:
        # 1. Buscar automáticamente cualquier archivo CSV que tenga la palabra 'Obras'
        lista_archivos = glob.glob("*Obras*.csv")
        
        if not lista_archivos:
            print("❌ ERROR: No se encontró ningún archivo CSV con la palabra 'Obras' en la carpeta.")
            print(f"Archivos actuales en la carpeta: {os.listdir('.')}")
            return

        archivo_encontrado = lista_archivos[0]
        print(f"📂 Archivo detectado: {archivo_encontrado}")

        # 2. Conectar a la base de datos
        conn = sqlite3.connect('municipio.db')
        
        # 3. Leer el CSV
        df = pd.read_csv(archivo_encontrado, encoding='latin-1')
        
        # 4. Limpieza de columnas
        df.columns = [c.strip() for c in df.columns]
        
        # 5. Guardar en la tabla 'obras'
        df.to_sql('obras', conn, if_exists='replace', index=False)
        
        conn.commit()
        conn.close()
        print(f"\n✅ ÉXITO: Los datos de '{archivo_encontrado}' se cargaron en la tabla 'obras'.")
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")

if __name__ == '__main__':
    reparar_definitivo()
