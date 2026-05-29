import sqlite3
from database import DB_GESTION

def listar_areas():
    conn = sqlite3.connect(DB_GESTION)
    cursor = conn.cursor()
    
    try:
        # Consultamos la tabla maestra de áreas
        cursor.execute("SELECT id, nombre, acuerdo_id FROM areas")
        areas = cursor.fetchall()
        
        if not areas:
            print("⚪ No hay áreas registradas todavía.")
            return

        print("\n--- ÁREAS REGISTRADAS EN LA DB ---")
        print(f"{'ID':<5} | {'NOMBRE DEL ÁREA':<30} | {'ID ACUERDO'}")
        print("-" * 50)
        for area in areas:
            print(f"{area[0]:<5} | {area[1]:<30} | {area[2]}")
            
    except sqlite3.Error as e:
        print(f"❌ Error al consultar: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    listar_areas()
