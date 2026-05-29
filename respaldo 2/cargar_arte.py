import sqlite3
import pandas as pd
import os

def importar_datos_arte():
    archivo_csv = 'base de datos Arte y Cultura.csv'
    base_datos = 'municipio.db'
    
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: No se encuentra '{archivo_csv}'")
        return

    try:
        # Leer CSV
        df = pd.read_csv(archivo_csv, encoding='latin-1')
        
        # Limpiar nombres de columnas para evitar duplicados y errores de SQL
        nuevas_cols = []
        counts = {}
        for col in df.columns:
            c_upper = str(col).strip().upper().replace(" ", "_")
            if c_upper in counts:
                counts[c_upper] += 1
                nuevas_cols.append(f"{c_upper}_{counts[c_upper]}")
            else:
                counts[c_upper] = 0
                nuevas_cols.append(c_upper)
        df.columns = nuevas_cols
        
        # Guardar en la base de datos
        conn = sqlite3.connect(base_datos)
        df.to_sql('arte_cultura', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
        print("✅ Base de datos actualizada con éxito.")
        
    except Exception as e:
        print(f"❌ Error al cargar: {e}")

if __name__ == "__main__":
    importar_datos_arte()
