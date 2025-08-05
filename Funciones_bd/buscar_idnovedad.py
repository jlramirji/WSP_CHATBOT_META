import json
import pyodbc
import os
import config

def buscar_idnovedad():
    """
    Busca el ID máximo de novedad en la tabla REPORTE_NOVEDADES
    """
    try:
        server = config.DB_SERVER
        database = config.DB_DATABASE
        driver = config.DB_DRIVER
        db_user = config.DB_USER
        db_password = config.DB_PASSWORD

        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={db_user};"
            f"PWD={db_password};"
            "TrustServerCertificate=yes;"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        sql = """
        SELECT max(idnovedad) as idnovedad
        FROM dbo.REPORTE_NOVEDADES;
        """
        cursor.execute(sql)
        row = cursor.fetchone()

        if row and row.idnovedad is not None:
            result = {"idnovedad": int(row.idnovedad)}
        else:
            result = {"idnovedad": None}

        print(f"🔍 ID de novedad encontrado: {json.dumps(result)}")
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        print(f"❌ Error al buscar ID de novedad: {e}")
        return None