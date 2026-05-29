import sqlite3

def crear_tabla_comude():
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    
    # Eliminamos si existe para actualizar estructura
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
            tipo_registro TEXT, -- Para diferenciar si es torneo comunitario, continuo o disciplina
            anio TEXT,
            trimestre TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Tabla COMUDE creada exitosamente.")

if __name__ == '__main__':
    crear_tabla_comude()
