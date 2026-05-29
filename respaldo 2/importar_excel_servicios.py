import sqlite3
import pandas as pd

def importar_datos_reales():
    # 1. Nombre del archivo que subiste (ajusta si el nombre es diferente en tu carpeta)
    archivo_csv = "base de datos nueva servicios publicos.xlsx - Hoja2.csv"
    
    try:
        # Leer el CSV (usamos la Hoja 2 que parece ser la que tiene los datos)
        # Saltamos la primera fila si es un encabezado extra o ajustamos según necesites
        df_excel = pd.read_csv(archivo_csv)
        
        # Conectar a la base de datos
        conn = sqlite3.connect('municipio.db')
        cursor = conn.cursor()

        # 2. Asegurar que la tabla existe con las 13 columnas de tu imagen
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

        # 3. Mapear los datos del Excel a nuestras columnas
        # Aquí ajustamos qué columna del Excel va a qué columna de la base de datos
        for _, fila in df_excel.iterrows():
            # Ejemplo de mapeo basado en tu archivo:
            # 'ACTIVIDAD' del excel -> 'tipo_de_servicio'
            # 'LOCALIDAD' del excel -> 'ubicacion_o_localidad'
            
            datos = (
                str(fila.get('ACTIVIDAD', 'Servicio General')),       # tipo_de_servicio
                f"Solicitud: {fila.get('SOLICITUDES REALIZADAS POR PARTE DE LA POBLACIÓN', 'N/A')}", # descripción
                str(fila.get('LOCALIDAD', 'Sin Ubicación')),          # ubicación
                "",                                                   # coordenadas_gps (vacío por ahora)
                str(fila.get('MES', '2026')),                         # fecha_de_reporte
                "",                                                   # fecha_de_atencion
                "Completado" if fila.get('CANTIDAD', 0) > 0 else "Pendiente", # estatus
                "Asignada",                                           # cuadrilla
                f"Inversión: {fila.get('INVERSION', 0)}",             # materiales/costo
                "",                                                   # foto antes
                "",                                                   # foto después
                f"Medida: {fila.get('UNIDAD DE MEDIDA', '')}"         # observaciones
            )

            cursor.execute('''
                INSERT INTO servicios_publicos (
                    tipo_de_servicio, descripcion_del_reporte, ubicacion_o_localidad, 
                    coordenadas_gps, fecha_de_reporte, fecha_de_atencion, 
                    estatus_de_atencion, cuadrilla_asignada, materiales_utilizados, 
                    evidencia_fotografica_antes, evidencia_fotografica_despues, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', datos)

        conn.commit()
        print(f"✅ Se han importado {len(df_excel)} registros desde el archivo CSV.")
        conn.close()

    except Exception as e:
        print(f"❌ Error al importar: {e}")

if __name__ == '__main__':
    importar_datos_reales()
