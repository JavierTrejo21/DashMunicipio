import sqlite3

def sincronizar_area():
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    # 1. Buscamos el ID del acuerdo de Igualdad y Derechos Humanos
    cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%IGUALDAD%'")
    acuerdo = cursor.fetchone()

    if acuerdo:
        id_acuerdo = acuerdo[0]
        
        # 2. Limpiamos cualquier rastro previo de Jurídico para evitar duplicados
        cursor.execute("DELETE FROM areas WHERE nombre LIKE '%Jurídica%' OR nombre LIKE '%Juridica%'")
        
        # 3. Insertamos el nombre exacto con el código 5.2
        cursor.execute("""
            INSERT INTO areas (codigo_informe, nombre, acuerdo_id) 
            VALUES ('5.2', '5.2 Unidad Jurídica', ?)
        """, (id_acuerdo,))
        
        conn.commit()
        print(f"✅ '5.2 Unidad Jurídica' vinculada al acuerdo ID {id_acuerdo} con éxito.")
    else:
        print("❌ No se encontró el acuerdo de IGUALDAD Y DERECHOS HUMANOS.")

    conn.close()

if __name__ == '__main__':
    sincronizar_area()
