import sqlite3

def dar_de_alta_area():
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    # 1. Buscamos el ID del acuerdo de Igualdad y Derechos Humanos
    # (Asumiendo que así se llama en tu base de datos)
    cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%IGUALDAD%'")
    resultado = cursor.fetchone()

    if resultado:
        acuerdo_id = resultado[0]
        # 2. Insertamos el área nueva vinculada a ese acuerdo
        # Usamos el nombre exacto para que el ruteador de app_municipio lo reconozca
        try:
            cursor.execute("""
                INSERT INTO areas (nombre, acuerdo_id) 
                VALUES (?, ?)
            """, ("5.1.3 LENGUAS INDÍGENAS", acuerdo_id))
            
            conn.commit()
            print("✅ Área '5.1.3 LENGUAS INDÍGENAS' dada de alta exitosamente.")
        except sqlite3.Error as e:
            print(f"❌ Error al insertar: {e}")
    else:
        print("❌ No se encontró el acuerdo 'IGUALDAD Y DERECHOS HUMANOS'. Revisa el nombre en la tabla acuerdos.")

    conn.close()

if __name__ == "__main__":
    dar_de_alta_area()
