import sqlite3

def importar_mis_datos():
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()

    # 1. Aseguramos que la tabla exista con tus columnas exactas
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

    # 2. LISTA DE TUS DATOS REALES
    # Sustituye los textos entre comillas por tu información real.
    # El orden es: Servicio, Descripción, Ubicación, GPS, Fecha Rep, Fecha Aten, Estatus, Cuadrilla, Materiales, Foto1, Foto2, Observaciones
    datos_a_cargar = [
        (
            'Alumbrado Público', 
            'Cambio de vapor de sodio por LED', 
            'Calle Juárez, Centro', 
            '20.021, -99.213', 
            '2026-04-01', 
            '2026-04-02', 
            'Completado', 
            'Cuadrilla A', 
            'Lámpara LED 100W, Cable duplex', 
            'antes.jpg', 
            'despues.jpg', 
            'Se cambió también el fotocontrol'
        ),
        # Puedes agregar más filas siguiendo el mismo formato:
        # ('Tipo', 'Desc', 'Ubic', 'GPS', 'F_Rep', 'F_At', 'Estatus', 'Cuad', 'Mat', 'Img1', 'Img2', 'Obs'),
    ]

    # 3. Insertar los datos
    # Limpiamos la tabla primero si quieres empezar de cero (Opcional):
    # cursor.execute("DELETE FROM servicios_publicos") 
    
    cursor.executemany('''
        INSERT INTO servicios_publicos (
            tipo_de_servicio, descripcion_del_reporte, ubicacion_o_localidad, 
            coordenadas_gps, fecha_de_reporte, fecha_de_atencion, 
            estatus_de_atencion, cuadrilla_asignada, materiales_utilizados, 
            evidencia_fotografica_antes, evidencia_fotografica_despues, observaciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', datos_a_cargar)

    conn.commit()
    conn.close()
    print(f"✅ Se han cargado {len(datos_a_cargar)} registros exitosamente.")

if __name__ == '__main__':
    importar_mis_datos()
