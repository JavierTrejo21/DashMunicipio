import sqlite3

def configurar_servicios():
    # 1. Conectar a la base de datos de datos operativos
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    
    # 2. Crear la tabla de Servicios Públicos con tus columnas exactas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios_publicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_de_servicio TEXT,
            descripcion_del_reporte TEXT,
            ubicacion_o_localidad TEXT,
            coordenadas_gps TEXT,
            fecha_de_reporte TEXT,
            fecha_de_atencion TEXT,
            estatus_de_atencion TEXT,
            cuadrilla_asignada TEXT,
            materiales_utilizados TEXT,
            evidencia_fotografica_antes TEXT,
            evidencia_fotografica_despues TEXT,
            observaciones TEXT
        )
    ''')
    
    # Insertar un dato de prueba para ver que funcione
    cursor.execute('''
        INSERT INTO servicios_publicos (tipo_de_servicio, descripcion_del_reporte, estatus_de_atencion)
        VALUES ('Alumbrado', 'Luminaria fundida en poste 45', 'Pendiente')
    ''')
    
    conn.commit()
    conn.close()

    # 3. Registrar el área en el menú principal (gestion_municipal.db)
    conn_menu = sqlite3.connect('gestion_municipal.db')
    cursor_menu = conn_menu.cursor()
    
    # Verificamos si ya existe el área de Servicios para no duplicar
    cursor_menu.execute("SELECT id FROM areas WHERE nombre LIKE '%Servicios%'")
    if not cursor_menu.fetchone():
        # Lo asignamos al Acuerdo 4 (Desarrollo Sostenible)
        cursor_menu.execute("INSERT INTO areas (codigo_informe, nombre, acuerdo_id) VALUES ('4.2', 'Servicios Públicos', 4)")
        conn_menu.commit()
    
    conn_menu.close()
    print("✅ Configuración completada con éxito.")

if __name__ == '__main__':
    configurar_servicios()
