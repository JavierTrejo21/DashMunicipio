import sqlite3

def crear_tabla_atencion():
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS atencion_ciudadana")
    
    cursor.execute('''
        CREATE TABLE atencion_ciudadana (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            area_o_localidad TEXT,
            cantidad INTEGER,
            actividad_tipo TEXT, -- 'CANALIZACION' o 'ATENCION_LOCALIDAD'
            anio TEXT,
            trimestre TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Tabla Atencion Ciudadana preparada.")

if __name__ == '__main__':
    crear_tabla_atencion()
