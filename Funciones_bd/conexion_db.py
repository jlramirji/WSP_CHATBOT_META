import pyodbc
import sys
import json

# Obtener el número de teléfono desde argumentos
#telefono = sys.argv[1]
telefono ='3015678901'

# Parámetros de conexión
server="CHEC-bdds04\checsqldes"
database="DM_SERVCORPORATIVOS"


# Cadena de conexión
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
)

#conexion = pyodbc.connect('DRIVER={SQL Server};SERVER=;DATABASE='+var.database+';Trusted_Connection=yes;')

# Crear cursor y ejecutar consulta
cursor = conn.cursor()
# cursor.execute(" SELECT * FROM DM_SERVCORPORATIVOS.TI.REPORTE_INCIDENTES where telefonoreportante = '3015678901'")


# Consulta SQL con parámetro
cursor.execute("SELECT * FROM DM_SERVCORPORATIVOS.TI.REPORTE_INCIDENTES WHERE telefonoreportante = ?", telefono)
#data = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]


for row in cursor.fetchall():
    print(row)

conn.close()

# Retornar como JSON
#print(json.dumps(data))
