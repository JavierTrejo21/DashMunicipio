import sqlite3

def configurar_unidad_juridica():
    # 1. Crear tabla en la base de datos operativa
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS juridico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            tipo_de_tramite TEXT,
            especificar_tramite TEXT,
            estatus TEXT,
            asesorias_juridicas INTEGER,
            convenios INTEGER,
            contratos INTEGER,
            escrituras INTEGER,
            costo_inversion REAL,
            beneficiarios INTEGER,
            observaciones TEXT,
            anio TEXT,
            trimestre TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # 2. Registrar con el nombre solicitado en el menú principal
    conn_menu = sqlite3.connect('gestion_municipal.db')
    cursor_menu = conn_menu.cursor()
    
    # Eliminamos registros anteriores con nombres parecidos para evitar duplicados
    cursor_menu.execute("DELETE FROM areas WHERE nombre LIKE '%Jurídic%'")
    
    # Insertamos el nombre oficial
    cursor_menu.execute("INSERT INTO areas (codigo_informe, nombre, acuerdo_id) VALUES ('1.2', 'Unidad Jurídica', 1)")
    
    conn_menu.commit()
    conn_menu.close()
    print("✅ Área registrada como 'Unidad Jurídica' exitosamente.")

if __name__ == '__main__':
    configurar_unidad_juridica()
