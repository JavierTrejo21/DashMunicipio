import sqlite3

def inyectar_datos_juridico():
    conn = sqlite3.connect('municipio.db')
    cursor = conn.cursor()
    
    # Datos de ejemplo basados en tu imagen
    datos = [
        ('ENERO', 'CONVENIO', 'Convenio de Colaboración UAEM', 'Concluido', 0, 1, 0, 0, 1500.00, 500, 'Firma en presidencia', '2026', '1er Trimestre'),
        ('FEBRERO', 'CONTRATO', 'Arrendamiento de Maquinaria', 'En Proceso', 0, 0, 1, 0, 45000.00, 2500, 'Revisión de cláusulas', '2026', '1er Trimestre'),
        ('MARZO', 'ASESORÍA', 'Atención ciudadana límites territoriales', 'Concluido', 15, 0, 0, 0, 0.00, 45, 'Asesoría gratuita', '2026', '1er Trimestre')
    ]
    
    cursor.executemany('''
        INSERT INTO juridico (mes, tipo_de_tramite, especificar_tramite, estatus, asesorias_juridicas, convenios, contratos, escrituras, costo_inversion, beneficiarios, observaciones, anio, trimestre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', datos)
    
    conn.commit()
    conn.close()
    print("✅ Datos de Jurídico cargados correctamente.")

if __name__ == '__main__':
    inyectar_datos_juridico()
