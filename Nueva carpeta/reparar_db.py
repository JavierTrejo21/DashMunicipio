import pandas as pd
import sqlite3
import os

def reparar_y_cargar():
    archivo_csv = 'datos.csv'
    base_datos = 'municipio.db'

    if not os.path.exists(archivo_csv):
        print(f"Error: No se encontró el archivo {archivo_csv}")
        return

    print(f">>> Leyendo {archivo_csv}...")
    
    # Leemos el CSV tal cual viene
    try:
        df = pd.read_csv(archivo_csv, encoding='latin1') 
    except:
        df = pd.read_csv(archivo_csv, encoding='utf-8')

    # LIMPIEZA AUTOMÁTICA DE NOMBRES DE COLUMNAS
    # Esto quita espacios y pone todo en minúsculas para que python no sufra
    df.columns = [c.lower().strip().replace(' ', '_').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u') for c in df.columns]
    
    print(f">>> Columnas detectadas: {list(df.columns)}")

    # LIMPIEZA DE DATOS (Pesos, Comas, Porcentajes)
    columnas_numericas = ['monto_total', 'beneficiarios', 'avance', 'avance_financiero']
    
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '', regex=False)\
                                         .str.replace(',', '', regex=False)\
                                         .str.replace('%', '', regex=False)\
                                         .str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # CARGA A SQLITE
    conn = sqlite3.connect(base_datos)
    # 'replace' asegura que si la tabla ya existía, se borre y se cree con la nueva estructura de 15 columnas
    df.to_sql('proyectos', conn, if_exists='replace', index=False)
    conn.close()

    print(f"\n>>> ¡ÉXITO! Se cargaron {len(df)} filas.")
    print(f">>> La base de datos ahora tiene {len(df.columns)} columnas.")

if __name__ == "__main__":
    reparar_y_cargar()
