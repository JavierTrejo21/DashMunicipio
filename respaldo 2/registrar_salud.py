import sqlite3

def registrar_salud_gestion():
    # Conectamos a la base de datos que controla el menú de botones
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    # Buscamos el ID del Acuerdo 2 (Bienestar y Prosperidad)
    # Usamos LIKE para que lo encuentre aunque varíen mayúsculas/minúsculas
    cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%BIENESTAR Y PROSPERIDAD%'")
    resultado = cursor.fetchone()

    if resultado:
        acuerdo_id = resultado[0]
        try:
            # Insertamos el nombre del área con su número
            cursor.execute("""
                INSERT INTO areas (nombre, acuerdo_id) 
                VALUES (?, ?)
            """, ("2.3 ENLACE DE SALUD", acuerdo_id))
            conn.commit()
            print("✅ ¡Éxito! El área '2.3 ENLACE DE SALUD' ha sido registrada.")
        except sqlite3.Error as e:
            print(f"⚠️ Nota: Es posible que el área ya esté registrada. (Error: {e})")
    else:
        print("❌ Error: No se encontró el Acuerdo 2. Verifica los nombres en tu base de datos.")

    conn.close()

if __name__ == "__main__":
    registrar_salud_gestion()
