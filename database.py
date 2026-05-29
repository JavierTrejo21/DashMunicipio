import sqlite3
import pandas as pd
import unicodedata
import re

DB_GESTION = 'gestion_municipal.db'

def normalizar_nombre_tabla(nombre):
    if not nombre: return "tabla_vacia"
    # Quitar acentos
    s = "".join(c for c in unicodedata.normalize('NFD', str(nombre)) if unicodedata.category(c) != 'Mn')
    s = s.strip().lower()
    # Reemplazar cualquier cosa que no sea letra o número por guion bajo
    s = re.sub(r'[^a-z0-9]', '_', s)
    # Evitar guiones bajos dobles
    s = re.sub(r'_+', '_', s)
    return s

def inicializar_db():
    conn = sqlite3.connect(DB_GESTION)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS acuerdos (id INTEGER PRIMARY KEY, nombre TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS areas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, acuerdo_id INTEGER)')
    cursor.execute("SELECT COUNT(*) FROM acuerdos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO acuerdos (id, nombre) VALUES (?, ?)", [(i, f"ACUERDO {i}") for i in range(1, 7)])
    conn.commit()
    conn.close()
