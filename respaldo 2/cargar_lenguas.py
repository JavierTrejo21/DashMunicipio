import sqlite3
import pandas as pd

def actualizar_bd_lenguas():
    archivo = 'base de datos nueva lenguas indigenas.csv'
    conn = sqlite3.connect('municipio.db')
    
    # Cargamos el nuevo CSV
    df = pd.read_csv(archivo, encoding='latin-1')
    
    # Limpieza básica de nombres de columnas para evitar errores de espacios
    df.columns = [c.strip() for c in df.columns]
    
    # Guardar en la tabla (sobrescribir)
    df.to_sql('lenguas_indigenas', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Base de datos actualizada con éxito (Nuevas columnas: MES e INVERSION).")

if __name__ == "__main__":
    actualizar_bd_lenguas()
