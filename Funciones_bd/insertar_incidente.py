import sys
import json
import pyodbc
from datetime import datetime
import os
import config

# Leer los datos JSON desde stdin
data = json.loads(sys.stdin.read())
#print("Datos recibidos:", data)

# Conexión
conn = pyodbc.connect(
    #'DRIVER={SQL Server};SERVER=CHEC-bdds04\\checsqldes;DATABASE=DM_SERVCORPORATIVOS;Trusted_Connection=yes;'
    DRIVER = config.DB_DRIVER,
    SERVER = config.DB_SERVER,
    DATABASE = config.DB_DATABASE,
    Trusted_Connection = config.DB_TRUSTED_CONNECTION,
)
cursor = conn.cursor()

# Insertar los datos usando parámetros seguros
query = """
INSERT INTO DM_SERVCORPORATIVOS.TI.REPORTE_INCIDENTES ( 
    nombrereportante, 
    cedulareportante, 
    codigoreportante,
    telefonoreportante, 
    nombrereportado, 
    cedulareportado, 
    codigoreportado,
    municipio,
    lugar,
    fechaincidente,
    fechahorareportado, 
    textoreporte
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
# Validar y formatear la fecha
fechaincidente = data['fechaincidente']
if fechaincidente:
    try:
        fecha_dt = datetime.strptime(fechaincidente, '%d/%m/%Y %H:%M')
        fechaincidente_sql = fecha_dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        fechaincidente_sql = None  # O maneja el error como prefieras
else:
    fechaincidente_sql = None
    
# Validar y formatear la fecha de reporte
fechareportado = data['fechahorareportado']

if fechareportado:
    try:
        fecha_sys = datetime.strptime(fechareportado, '%d/%m/%Y %H:%M:%S')
        fechareportado_sql = fecha_sys.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        fechareportado_sql = None  # O maneja el error como prefieras
else:
    fechareportado_sql = None

params = (
    data['nombrereportante'],
    data['cedulareportante'],
    data['codigoreportante'],
    data['telefonoreportante'],
    data['nombrereportado'],
    data['cedulareportado'],
    data['codigoreportado'],
    data['municipio'],
    data['lugar'],
    fechaincidente_sql,
    fechareportado_sql,
    data['textoreporte']
)

cursor.execute(query, params)
conn.commit()
conn.close()

print("Inserción exitosa")
