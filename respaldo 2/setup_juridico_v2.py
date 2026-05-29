import sqlite3

def actualizar_tabla_juridico():
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    
    # Eliminamos la tabla anterior para crear la nueva con la estructura del CSV
    cursor.execute("DROP TABLE IF EXISTS juridico")
    
    cursor.execute('''
        CREATE TABLE juridico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            localidad TEXT,
            descripcion TEXT,
            asesoria_tenencia INTEGER,
            asesoria_civil_familiar INTEGER,
            juicios_obras INTEGER,
            canalizaciones_pension INTEGER,
            correcciones_actas INTEGER,
            convenios_contratos INTEGER,
            audiencias_conciliador INTEGER,
            visitaduria_agraria INTEGER,
            catastro_deslindes INTEGER,
            actas_registro_civil INTEGER,
            revision_padron INTEGER,
            traslados_dominio INTEGER,
            revision_avaluos INTEGER,
            deslindes_area INTEGER,
            anio TEXT,
            trimestre TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Tabla Jurídico actualizada con la nueva estructura de columnas.")

if __name__ == '__main__':
    actualizar_tabla_juridico()
