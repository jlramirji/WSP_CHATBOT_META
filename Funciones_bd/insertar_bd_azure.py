import pyodbc
from datetime import datetime, timedelta
import os
import config

def formatear_fecha(fecha_str):
    # Convierte 'dd-mm-yyyy' a 'yyyy-mm-dd'
    if not fecha_str:
        return None
    try:
        fecha = datetime.strptime(fecha_str, "%d-%m-%Y")
        return fecha.strftime("%d/%m/%Y")
    except ValueError:
        return fecha_str  # Si ya está en formato 'yyyy-mm-dd'

def formatear_fecha_hora_colombia(fecha_hora_str):
    # Convierte 'dd-mm-yyyy HH:MM:SS' a 'yyyy-mm-dd HH:MM:SS' en zona horaria Colombia (UTC-5)
    if not fecha_hora_str:
        return None
    try:
        fecha, hora = fecha_hora_str.split(' ')
        dt = datetime.strptime(fecha + ' ' + hora, "%d-%m-%Y %H:%M:%S")
        # Ajusta a UTC-5 (Colombia)
        dt_colombia = dt - timedelta(hours=5)
        return dt_colombia.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return fecha_hora_str  # Si ya está en formato correcto

def insertar_incidente(incidente_data):
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={config.DB_SERVER};"
        f"DATABASE={config.DB_DATABASE};"
        f"UID={config.DB_USER};"
        f"PWD={config.DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    fechanovedad_sql = formatear_fecha(incidente_data.get('fechaincidente'))
    fechareportado_sql = formatear_fecha_hora_colombia(incidente_data.get('fechahorareportado'))

    query = """
        INSERT INTO dbo.REPORTE_NOVEDADES (
            nombrereportante, 
            cedulareportante, 
            codigoreportante,
            telefonoreportante, 
            nombrereportado, 
            cedulareportado, 
            codigoreportado,
            municipio,
            lugar,
            fechanovedad,
            fechahorareportado, 
            textoreporte,
            adjuntos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        query,
        incidente_data.get('nombrereportante', ''),
        incidente_data.get('cedulareportante', ''),
        incidente_data.get('codigoreportante', ''),
        incidente_data.get('telefonoreportante', ''),
        incidente_data.get('nombrereportado', ''),
        incidente_data.get('cedulareportado', ''),
        incidente_data.get('codigoreportado', ''),
        incidente_data.get('municipio', ''),
        incidente_data.get('lugar', ''),
        fechanovedad_sql,
        fechareportado_sql,
        incidente_data.get('textoreporte', ''),
        incidente_data.get('adjuntos', '')
    )
    conn.commit()
    
    # Obtener el ID del incidente recién insertado
    incidente_id = None
    try:
        cursor.execute("SELECT SCOPE_IDENTITY() as id")
        row = cursor.fetchone()
        if row:
            incidente_id = int(row.id)
            print(f' ** ID del incidente: {incidente_id} **')
    except Exception as e:
        print(f' ** Error al obtener ID: {e} **')
    
    cursor.close()
    conn.close()
    print(' ** Inserción exitosa **')
    print(' ** -------------------------------------- **')
    return incidente_id
