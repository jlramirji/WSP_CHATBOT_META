import sys
import json
import pyodbc
from decimal import Decimal
import os
import pandas as pd
import config

#telefono=573137182944

server = config.DB_SERVER
database = config.DB_DATABASE
driver = config.DB_DRIVER
db_user = config.DB_USER
db_password = config.DB_PASSWORD

#conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={db_user};PWD={db_password}"
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={db_user};"
    f"PWD={db_password};"
    "TrustServerCertificate=yes;"
)

# Consulta
def BuscarNombrexTelefono(telefono):
    # Conexión y consulta
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # sql = """
    # SELECT DISTINCT nombrereportante
    # FROM DM_SERVCORPORATIVOS.TI.REPORTE_NOVEDADES
    # WHERE telefonoreportante = ?
    # """
    sql = """
    SELECT DISTINCT nombrereportante,cedulareportante,codigoreportante
    FROM dbo.REPORTE_NOVEDADES
    WHERE telefonoreportante = ?
    """
    cursor.execute(sql, telefono)
    #row = cursor.fetchone()

    for row in cursor.fetchall():
        nombre_texto, cedula_texto, usuario_texto = row
        return nombre_texto, cedula_texto, usuario_texto
    cursor.close()
    conn.close()


#resultado = BuscarNombrexTelefono(573137182944)

# # Convertir a DataFrame
# df = pd.DataFrame([resultado], columns=['nombre'])

# # Extraer el texto del campo 'nombre'
# nombre_texto = df['nombre'].iloc[0]
#print(resultado)


##  HABILITAR PARA PROBAR LOCALMENTE
# Nombre=BuscarNombrexTelefono(telefono)
# print(f"El nombre es: {Nombre[0]}")
# print(f"El cedula es: {Nombre[1]}")
# print(f"El usuario es: {Nombre[2]}")

