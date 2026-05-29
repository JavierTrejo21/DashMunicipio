import sqlite3

# Nombre de tu base de datos
DB_GESTION = 'gestion_municipal.db'

def limpieza_absoluta():
    conn = sqlite3.connect(DB_GESTION)
    cursor = conn.cursor()
    
    try:
        # 1. Obtener los nombres de TODAS las tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        tablas_a_borrar = []
        for (nombre,) in tablas:
            # NO borramos las tablas maestras ni las del sistema
            if nombre not in ['acuerdos', 'areas', 'sqlite_sequence']:
                tablas_a_borrar.append(nombre)
        
        # 2. Borrar las tablas de datos (CON COMILLAS DOBLES)
        for tabla in tablas_a_borrar:
            # Ponemos el nombre entre "" para evitar el error de sintaxis con números o puntos
            cursor.execute(f'DROP TABLE IF EXISTS "{tabla}"')
            print(f"🗑️ Tabla de datos '{tabla}' eliminada.")

        # 3. Limpiar los registros administrativos
        cursor.execute("DELETE FROM areas")
        # Reiniciar los contadores de ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='areas'")
        
        conn.commit()
        print("\n✨ LIMPIEZA TOTAL COMPLETADA.")
        print("Se han mantenido los acuerdos, pero todas las áreas y sus datos fueron borrados.")

    except Exception as e:
        print(f"❌ Error crítico durante la limpieza: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    limpieza_absoluta()
