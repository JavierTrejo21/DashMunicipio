import sqlite3
conn = sqlite3.connect('municipio.db')
cursor = conn.execute('select * from proyectos')
names = [description[0] for description in cursor.description]
print("Las columnas reales en la DB son:", names)
conn.close()
