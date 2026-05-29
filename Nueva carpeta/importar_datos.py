import sqlite3
import pandas as pd

def importar_datos_municipio():
    # 1. Conexión a la base de datos
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()

    # 2. Leer el archivo consolidado
    # Asegúrate de haber guardado el Excel como CSV
    try:
        df = pd.read_csv('datos_maestros.csv', encoding='utf-8')
    except:
        df = pd.read_csv('datos_maestros.csv', encoding='latin1')

    # 3. Limpieza básica de datos antes de subir
    df['MONTO'] = pd.to_numeric(df['MONTO'], errors='coerce').fillna(0)
    df['BENEFICIARIOS'] = pd.to_numeric(df['BENEFICIARIOS'], errors='coerce').fillna(0)
    df['META_VAL'] = pd.to_numeric(df['META_VAL'], errors='coerce').fillna(0)

    # 4. Crear o Reemplazar la tabla 'proyectos'
    # Usamos 'replace' para que cada vez que corras el script se actualice con lo más nuevo
    df.to_sql('proyectos', conn, if_exists='replace', index=False)

    conn.close()
    print("✅ ¡Éxito! La base de datos ha sido actualizada con todas las áreas.")

if __name__ == "__main__":
    importar_datos_municipio()
