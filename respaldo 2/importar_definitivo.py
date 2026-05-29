import sqlite3
import pandas as pd
import os
import glob

def importar_con_codificacion_correcta():
    # 1. Buscar el archivo CSV en la carpeta
    patron = os.path.join("C:\\DashMunicipio", "*servicios publicos*.csv")
    archivos = glob.glob(patron)

    if not archivos:
        print("❌ ERROR: No se encontró ningún archivo .csv en C:\\DashMunicipio")
        return

    archivo_encontrado = archivos[0]
    print(f"📂 Archivo detectado: {archivo_encontrado}")

    try:
        # 2. Leer datos probando codificación Latin-1 (típica de Excel en español)
        df = pd.read_csv(archivo_encontrado, encoding='latin-1')
        df.columns = df.columns.str.strip() # Limpiar espacios en nombres de columnas

        # 3. Filtrar solo filas con actividad real (CANTIDAD > 0)
        # Esto evita cargar las filas vacías que vimos en tu archivo
        df_real = df[df['CANTIDAD'] > 0].copy()

        if df_real.empty:
            print("⚠️ El archivo se leyó pero no contiene registros con CANTIDAD mayor a 0.")
            return

        # 4. Conectar a la base de datos municipio.db
        conn = sqlite3.connect('municipio.db')
        cursor = conn.cursor()

        # Asegurar que la tabla servicios_publicos tenga las 13 columnas de tu imagen
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

        # Limpiar la tabla antes de la carga completa
        cursor.execute("DELETE FROM servicios_publicos")

        # 5. Insertar los datos mapeando las columnas de tu CSV
        for _, fila in df_real.iterrows():
            datos = (
                str(fila.get('ACTIVIDAD', 'General')),
                str(fila.get('SOLICITUDES REALIZADAS POR PARTE DE LA POBLACIÓN', 'Reporte Ciudadano')),
                str(fila.get('LOCALIDAD', 'MUNICIPAL')),
                "", # coordenadas_gps
                str(fila.get('MES', '')),
                "", # fecha_de_atencion
                "Completado", # estatus (asumido ya que hay cantidad)
                "Cuadrilla Municipal",
                f"Inversión: ${fila.get('INVERSION', 0):,.2f}",
                "", # foto_antes
                "", # foto_despues
                f"Unidad: {fila.get('UNIDAD DE MEDIDA', '')}" # observaciones
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
        conn.close()
        print(f"✅ ¡ÉXITO TOTAL! Se cargaron {len(df_real)} registros reales de tu archivo.")

    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

if __name__ == '__main__':
    importar_con_codificacion_correcta()
