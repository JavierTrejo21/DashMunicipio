import sqlite3

def vincular_atencion():
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    # Buscamos el acuerdo de Igualdad
    cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%IGUALDAD%'")
    acuerdo = cursor.fetchone()

    if acuerdo:
        id_acuerdo = acuerdo[0]
        # Borramos si existe para evitar duplicados
        cursor.execute("DELETE FROM areas WHERE nombre LIKE '%Atencion Ciudadana%'")
        # Insertamos con el código solicitado
        cursor.execute("""
            INSERT INTO areas (codigo_informe, nombre, acuerdo_id) 
            VALUES ('5.1.2', '5.1.2 Atencion Ciudadana', ?)
        """, (id_acuerdo,))
        conn.commit()
        print(f"✅ Área vinculada correctamente bajo el ID {id_acuerdo}")
    else:
        print("❌ No se encontró el acuerdo correspondiente.")
    conn.close()

if __name__ == '__main__':
    vincular_atencion()
