import sqlite3
from database import DB_GESTION, normalizar_nombre_tabla

def eliminar_area_directa(id_area=None, nombre_area=None):
    """
    Elimina un área buscando por ID o por Nombre exacto.
    """
    conn = sqlite3.connect(DB_GESTION)
    cursor = conn.cursor()
    
    try:
        # 1. Localizar el área
        if id_area:
            cursor.execute("SELECT id, nombre FROM areas WHERE id = ?", (id_area,))
        elif nombre_area:
            cursor.execute("SELECT id, nombre FROM areas WHERE nombre = ?", (nombre_area.upper(),))
        else:
            print("❌ Debes proporcionar un ID o un Nombre.")
            return

        resultado = cursor.fetchone()
        
        if not resultado:
            print("⚠️ No se encontró el área en la base de datos.")
            return

        a_id, a_nombre = resultado
        tabla_fisica = normalizar_nombre_tabla(a_nombre)

        # 2. Borrar la tabla de datos (donde están las filas de Excel)
        cursor.execute(f"DROP TABLE IF EXISTS {tabla_fisica}")
        print(f"🗑️ Tabla física '{tabla_fisica}' eliminada.")

        # 3. Borrar el registro de la tabla 'areas'
        cursor.execute("DELETE FROM areas WHERE id = ?", (a_id,))
        print(f"✅ Registro de área '{a_nombre}' eliminado de la lista maestra.")

        conn.commit()
        print("🚀 Operación completada con éxito.")

    except Exception as e:
        print(f"❌ Error durante la eliminación: {e}")
    finally:
        conn.close()

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # Opción A: Por ID (puedes ver el ID en tu tabla de SQL)
    # eliminar_area_directa(id_area=5) 

    # Opción B: Por Nombre exacto
    area_a_borrar = input("Ingresa el nombre del área que quieres borrar permanentemente: ")
    eliminar_area_directa(nombre_area=area_a_borrar)
