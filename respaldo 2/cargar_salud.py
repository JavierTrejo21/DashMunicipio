import sqlite3
import pandas as pd
import os

def importar_datos_salud():
    archivo_csv = 'base de datos Enlace de Salud.csv'
    base_datos = 'municipio.db'
    
    # Verificar si el archivo CSV existe en la carpeta
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: No se encuentra el archivo '{archivo_csv}' en la carpeta.")
        return

    try:
        # Cargamos el CSV (usando latin-1 por los acentos)
        df = pd.read_csv(archivo_csv, encoding='latin-1')
        
        # Limpiamos espacios en los nombres de las columnas
        df.columns = [c.strip() for c in df.columns]
        
        # Conectamos a la base de datos de los datos (municipio.db)
        conn = sqlite3.connect(base_datos)
        
        # Creamos la tabla 'enlace_salud'
        df.to_sql('enlace_salud', conn, if_exists='replace', index=False)
        
        conn.commit()
        conn.close()
        print(f"✅ ¡Éxito! Se han cargado {len(df)} registros en la tabla 'enlace_salud'.")
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

if __name__ == "__main__":
    importar_datos_salud()
