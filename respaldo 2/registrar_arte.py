import sqlite3

def registrar_arte_gestion():
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    # Buscamos el ID del Acuerdo 3
    cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%DESARROLLO ECONÓMICO Y CULTURAL%'")
    resultado = cursor.fetchone()

    if resultado:
        acuerdo_id = resultado[0]
        try:
            cursor.execute("""
                INSERT INTO areas (nombre, acuerdo_id) 
                VALUES (?, ?)
            """, ("3.4 ARTE Y CULTURA", acuerdo_id))
            conn.commit()
            print("✅ Área '3.4 ARTE Y CULTURA' registrada en el Acuerdo 3.")
        except sqlite3.Error as e:
            print(f"⚠️ El área ya existe o hubo un error: {e}")
    else:
        print("❌ No se encontró el Acuerdo 3.")

    conn.close()

if __name__ == "__main__":
    registrar_arte_gestion()
