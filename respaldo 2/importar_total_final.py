import sqlite3
import pandas as pd
import os
import glob

def importar_todo_sin_filtros():
    # 1. Buscar el archivo CSV
    patron = os.path.join("C:\\DashMunicipio", "*servicios publicos*.csv")
    archivos = glob.glob(patron)

    if not archivos:
        print("❌ ERROR: No se encontró el archivo CSV en C:\\DashMunicipio")
        return

    archivo_encontrado = archivos[0]
    print(f"📂 Procesando archivo completo: {archivo_encontrado}")

    try:
        # 2. Leer con codificación Latin-1 para evitar errores de tildes
        df = pd.read_csv(archivo_encontrado, encoding='latin-1')
        df.columns = df.columns.str.strip()

        # 3. Limpieza de datos
        # Convertimos Inversión y Beneficiarios a números, llenando vacíos con 0
        df['INVERSION'] = pd.to_numeric(df['INVERSION'], errors='coerce').fillna(0)
        df['BENEFICIARIOS'] = pd.to_numeric(df['BENEFICIARIOS'], errors='coerce').fillna(0)
        df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0)

        # 4. Conectar a la base de datos
        conn = sqlite3.connect('municipio.db')
        cursor = conn.cursor()

        # Asegurar tabla de 13 columnas
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

        # Limpiar para carga total
        cursor.execute("DELETE FROM servicios_publicos")

        # 5. Insertar TODOS los registros (más de 1400)
        registros_cargados = 0
        for _, fila in df.iterrows():
            # Solo saltamos si la fila está completamente vacía
            if pd.isna(fila.get('LOCALIDAD')) and pd.isna(fila.get('ACTIVIDAD')):
                continue

            datos = (
                str(fila.get('ACTIVIDAD', 'Sin clasificar')),
                f"Solicitudes: {fila.get('SOLICITUDES REALIZADAS POR PARTE DE LA POBLACIÓN', 0)}",
                str(fila.get('LOCALIDAD', 'MUNICIPAL')),
                "", # GPS
                str(fila.get('MES', 'S/M')),
                "", # Fecha atención
                "Finalizado" if fila.get('CANTIDAD', 0) > 0 else "Registrado",
                "Personal Municipal",
                str(fila.get('INVERSION', 0)), # Guardamos el número puro para el dashboard
                "", # Foto antes
                "", # Foto despues
                f"Beneficiarios: {fila.get('BENEFICIARIOS', 0)} | Unidad: {fila.get('UNIDAD DE MEDIDA', '')}"
            )

            cursor.execute('''
                INSERT INTO servicios_publicos (
                    tipo_de_servicio, descripcion_del_reporte, ubicacion_o_localidad, 
                    coordenadas_gps, fecha_de_reporte, fecha_de_atencion, 
                    estatus_de_atencion, cuadrilla_asignada, materiales_utilizados, 
                    evidencia_fotografica_antes, evidencia_fotografica_despues, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', datos)
            registros_cargados += 1

        conn.commit()
        conn.close()
        print(f"✅ CARGA COMPLETA: {registros_cargados} registros procesados.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == '__main__':
    importar_todo_sin_filtros()
