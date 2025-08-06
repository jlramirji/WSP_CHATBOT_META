#!/usr/bin/env python3
"""
Ejemplo de uso del nuevo sistema de configuración
Este archivo muestra cómo usar las variables de configuración desde config.py
"""

import config

def ejemplo_uso_configuracion():
    """
    Ejemplo de cómo usar las variables de configuración
    """
    print("=== Ejemplo de Uso del Sistema de Configuración ===\n")
    
    # Ejemplo de configuración de WhatsApp
    print("🔵 Configuración de WhatsApp:")
    print(f"   Token: {config.WHATSAPP_ACCESS_TOKEN[:20]}..." if len(config.WHATSAPP_ACCESS_TOKEN) > 20 else f"   Token: {config.WHATSAPP_ACCESS_TOKEN}")
    print(f"   Phone ID: {config.WHATSAPP_PHONE_ID}")
    print(f"   API URL: {config.WHATSAPP_API_URL}")
    print()
    
    # Ejemplo de configuración de base de datos
    print("🟢 Configuración de Base de Datos:")
    print(f"   Driver: {config.DB_DRIVER}")
    print(f"   Servidor: {config.DB_SERVER}")
    print(f"   Base de datos: {config.DB_DATABASE}")
    print(f"   Usuario: {config.DB_USER}")
    print(f"   Conexión confiable: {config.DB_TRUSTED_CONNECTION}")
    print()
    
    # Ejemplo de configuración de Azure
    print("🟡 Configuración de Azure Speech:")
    print(f"   Key: {config.AZURE_SPEECH_KEY[:20]}..." if len(config.AZURE_SPEECH_KEY) > 20 else f"   Key: {config.AZURE_SPEECH_KEY}")
    print(f"   Región: {config.AZURE_SPEECH_REGION}")
    print()
    
    # Ejemplo de configuración del servidor
    print("🟠 Configuración del Servidor:")
    print(f"   Puerto: {config.PORT}")
    print()
    
    # Ejemplo de directorios
    print("🟣 Directorios de Archivos:")
    print(f"   Carpeta de upload: {config.UPLOAD_FOLDER}")
    print(f"   Carpeta de adjuntos: {config.ADJUNTOS_FOLDER}")
    print()
    
    # Ejemplo de validación de configuración
    print("✅ Validación de Configuración:")
    configuraciones_requeridas = [
        ('WHATSAPP_ACCESS_TOKEN', config.WHATSAPP_ACCESS_TOKEN),
        ('DB_SERVER', config.DB_SERVER),
        ('DB_DATABASE', config.DB_DATABASE),
        ('AZURE_SPEECH_KEY', config.AZURE_SPEECH_KEY),
        ('AZURE_SPEECH_REGION', config.AZURE_SPEECH_REGION)
    ]
    
    for nombre, valor in configuraciones_requeridas:
        if valor and valor != f"tu_{nombre.lower()}_aqui":
            print(f"   ✅ {nombre}: Configurado")
        else:
            print(f"   ❌ {nombre}: No configurado")
    
    print("\n=== Fin del Ejemplo ===")

def ejemplo_conexion_bd():
    """
    Ejemplo de cómo usar la configuración para conectar a la base de datos
    """
    print("\n=== Ejemplo de Conexión a Base de Datos ===")
    
    try:
        import pyodbc
        
        # Construir string de conexión usando config.py
        conn_str = (
            f"DRIVER={{{config.DB_DRIVER}}};"
            f"SERVER={config.DB_SERVER};"
            f"DATABASE={config.DB_DATABASE};"
            f"UID={config.DB_USER};"
            f"PWD={config.DB_PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        
        print(f"String de conexión: {conn_str}")
        print("✅ String de conexión generado correctamente")
        
        # Nota: No se ejecuta la conexión real para evitar errores
        # conn = pyodbc.connect(conn_str)
        
    except ImportError:
        print("❌ pyodbc no está instalado")
    except Exception as e:
        print(f"❌ Error: {e}")

def ejemplo_whatsapp_api():
    """
    Ejemplo de cómo usar la configuración para WhatsApp API
    """
    print("\n=== Ejemplo de WhatsApp API ===")
    
    try:
        import requests
        
        # Ejemplo de headers para WhatsApp API
        headers = {
            "Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        print(f"Headers configurados: {headers}")
        print("✅ Headers de WhatsApp API configurados correctamente")
        
        # URL de ejemplo
        url = f"{config.WHATSAPP_API_URL}/messages"
        print(f"URL de ejemplo: {url}")
        
    except ImportError:
        print("❌ requests no está instalado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ejemplo_uso_configuracion()
    ejemplo_conexion_bd()
    ejemplo_whatsapp_api()
    
    print("\n" + "="*50)
    print("💡 Para usar este sistema en tu código:")
    print("   1. Importa config: import config")
    print("   2. Usa las variables: config.WHATSAPP_ACCESS_TOKEN")
    print("   3. Edita config.py con tus valores reales")
    print("="*50) 