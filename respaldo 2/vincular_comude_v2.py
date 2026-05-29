import sqlite3

def configurar_jerarquia_comude():
    # Conectamos a la base de datos de navegación
    conn = sqlite3.connect('gestion_municipal.db')
    cursor = conn.cursor()

    try:
        # 1. Buscamos el ID del acuerdo de IGUALDAD Y DERECHOS HUMANOS
        cursor.execute("SELECT id FROM acuerdos WHERE nombre LIKE '%IGUALDAD%'")
        acuerdo = cursor.fetchone()

        if acuerdo:
            id_acuerdo = acuerdo[0]
            
            # 2. Eliminamos registros previos para evitar duplicados
            cursor.execute("DELETE FROM areas WHERE nombre LIKE '%COMUDE%'")
            
            # 3. Insertamos con la nueva nomenclatura
            cursor.execute("""
                INSERT INTO areas (codigo_informe, nombre, acuerdo_id) 
                VALUES ('5.1.1', '5.1.1 Comude', ?)
            """, (id_acuerdo,))
            
            conn.commit()
            print(f"✅ ÉXITO: COMUDE configurado como '5.1.1 Comude' bajo el acuerdo ID {id_acuerdo}")
        else:
            print("❌ ERROR: No se encontró el acuerdo de IGUALDAD Y DERECHOS HUMANOS.")
            
    except Exception as e:
        print(f"❌ ERROR de base de datos: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    configurar_jerarquia_comude()
