import sqlite3

def vincular_area_acuerdo():
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    # 1. Buscamos el ID del acuerdo de Derechos Humanos
    cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%IGUALDAD Y DERECHOS HUMANOS%'")
    resultado = cursor.fetchone()

    if resultado:
        id_acuerdo = resultado[0]
        
        # 2. Verificamos si la Unidad Jurídica ya existe para actualizarla o crearla
        cursor.execute("SELECT id FROM areas WHERE nombre = 'Unidad Jurídica'")
        area_existente = cursor.fetchone()

        if area_existente:
            # Si ya existe, solo cambiamos su acuerdo_id
            cursor.execute("UPDATE areas SET acuerdo_id = ?, codigo_informe = '1.2' WHERE nombre = 'Unidad Jurídica'", (id_acuerdo,))
            print(f"✅ Unidad Jurídica movida al acuerdo ID: {id_acuerdo}")
        else:
            # Si no existe, la creamos vinculada a ese acuerdo
            cursor.execute("INSERT INTO areas (codigo_informe, nombre, acuerdo_id) VALUES ('1.2', 'Unidad Jurídica', ?)", (id_acuerdo,))
            print(f"✅ Unidad Jurídica creada en el acuerdo ID: {id_acuerdo}")
    else:
        print("❌ No se encontró el acuerdo 'PARA LA IGUALDAD Y DERECHOS HUMANOS'. Verifica el nombre en la tabla 'acuerdos'.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    vincular_area_acuerdo()
