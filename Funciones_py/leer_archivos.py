import csv
import os
 
csv_folder = os.path.join(os.path.dirname(__file__), '..', 'csv_file')
archivo1 = os.path.join(csv_folder, 'Archivo1.csv')
archivo2 = os.path.join(csv_folder, 'Archivo2.csv')
archivo3 = os.path.join(csv_folder, 'Archivo3.csv')
 
def leer_archivo_csv(ruta_archivo):
    datos = []
    with open(ruta_archivo, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre = row.get("DisplayName", "")
            cedula = row.get("EmployeeID", "")
            usuario = row.get("SamAccountName", "")
            correo = row.get("UserPrincipalName", "")
            datos.append({
                "nombre": nombre,
                "cedula": cedula,
                "usuario": usuario,
                "correo": correo
            })
    return datos
 
def buscar_por_nombre(nombre_buscado):
    datos_archivo1 = leer_archivo_csv(archivo1)
    datos_archivo2 = leer_archivo_csv(archivo2)
    datos_archivo3 = leer_archivo_csv(archivo3)
    datos_combinados = datos_archivo1 + datos_archivo2 + datos_archivo3
 
    palabras_buscadas = [p.lower() for p in nombre_buscado.split() if p.strip() != ""]
    resultados = []
    for dato in datos_combinados:
        nombre_completo = dato["nombre"].lower()
        if all(palabra in nombre_completo for palabra in palabras_buscadas):
            resultados.append(dato)
    return resultados
 
# Ejemplo de uso:
if __name__ == "__main__":
    nombre = input("Ingrese el nombre a buscar: ")
    resultados = buscar_por_nombre(nombre)
    for r in resultados:
        print(r)