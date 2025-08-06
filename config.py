import pandas as pd
from datetime import datetime

# Configuración de variables de entorno para el proyecto WhatsApp WebMeta
# Este archivo centraliza todas las configuraciones del proyecto

# TOKEN PERMANENTE WHATSAPP CHATBOTCHEC
# WHATSAPP_ACCESS_TOKEN = EAAU6sySSA20BO8ZA4ZAW4TiBnQcXXvxZCtprZB3ZApdSJI4u2YBg9GF9ZBvKX3n3JcSvLK2LWfD24G8QZAn4sZB2yBGP1UlbMkWz1ZBEv1wkTClF0VwZA7NpdioFB9OZBO0sgpYDmdGy6qDATAi0yeC9aTnKBlKrZCR9i18QoX5ydt7VYVsKnGdG9SXlpZCzr2G7ZBehp2jAZDZD
# WHATSAPP_PHONE_ID=662597943605166
# VERIFY_TOKEN = "78SAJSNJANS76S8DSHBSBSDS"

# TOKEN PERMANENTE WHATSAPP BUILDERBOT
# Configuración de WhatsApp Business API
# WHATSAPP_ACCESS_TOKEN = "EAAO4qdmmXbQBPM69Bhcz8kEuTLgHowZCcdobZBZAq6Wa54pOEOYoqLzl6nVnZBDRWMnGdsHpBuaREdoZC8QSNMQpqv6fbLEEqOoZCWxnIEow53rc4CCf0G5X6LSGrLos58ubGp9vm9T0EvDZCO9AkwxYvIdyXUufAvyisxAwl2A1Gmkmg4ZCQoIWYBksKeQKBBHbxAZDZD"
# WHATSAPP_PHONE_ID = "662597943605166"
# VERIFY_TOKEN = "78SAJSNJANS76S8DSHBSBSDS"
# WEBHOOK_URL = https://whatsapp-python-webmeta-hxfmfeaad9e2ckhf.eastus2-01.azurewebsites.net/whatsapp # URL DE AZURE APP SERVICE Whatsapp-python-webmeta

# TOKEN TEMPORAL WHATSAPP APP CHATBOTNOVEDADES
# WHATSAPP_ACCESS_TOKEN = "EAARzIkmzFGIBPAA6rterjdJjkFeZCX5y9C37ZBodIyHvpVN9ZCQ0y9zkSfmjo8gojHHKXGKdLdMQNg5h9dSEQwQVKMOsg82C2Cgq2A4UT6d01uxQyJt8GYW8R8YkhVsAIAKIB5BQ9OM5mYpAXXWGUSalKzt5BGVZB1pphxZAXzzIDxWHqhoDWF3iuIpo8lbql7uy7S2HeIPKNfNzvOaIxFFaec5hcWzHvOF8OQB8ceHxZBomMvMrhBfpNR8V4ZD"
# WHATSAPP_PHONE_ID = "657826577424576"
# VERIFY_TOKEN = "78SAJSNJA"

WHATSAPP_ACCESS_TOKEN = "EAAO4qdmmXbQBPM69Bhcz8kEuTLgHowZCcdobZBZAq6Wa54pOEOYoqLzl6nVnZBDRWMnGdsHpBuaREdoZC8QSNMQpqv6fbLEEqOoZCWxnIEow53rc4CCf0G5X6LSGrLos58ubGp9vm9T0EvDZCO9AkwxYvIdyXUufAvyisxAwl2A1Gmkmg4ZCQoIWYBksKeQKBBHbxAZDZD"
WHATSAPP_PHONE_ID = "662597943605166"
VERIFY_TOKEN = "78SAJSNJANS76S8DSHBSBSDS"
#VERIFY_TOKEN = "78SAJSNJANS76S8DSHBSBSDS"

# Configuración del servidor
PORT = 3000

#Ruta de archivos de DA
rutaCompartida = "\\chec-apd09\\Ejecutables\\DA"

# Variables de entorno para la base de datos SQL SERVER
DB_DRIVER="ODBC Driver 18 for SQL Server"
# DB_SERVER=CHEC-bdds04\checsqldes
# DB_DATABASE=DM_SERVCORPORATIVOS
# DB_USER=intdmservcorporativos
# DB_PASSWORD=JfxwLrc4rTM8w*
# #DB_TRUSTED_CONNECTION=Yes
DB_TRUST_SERVER_CERTIFICATE="Yes"

# Configuración de base de datos AZURE
DB_SERVER = "servidorchatbot2.database.windows.net"
DB_DATABASE = "chatbotbdmeta2"
DB_USER = "adminjorge"
DB_PASSWORD = "Azuresql2025*"
DB_TRUSTED_CONNECTION = "yes"
DB_TRUST_SERVER_CERTIFICATE="Yes"

# Configuración de Azure Speech-to-Text
AZURE_SPEECH_KEY = "EJu1IBSNdmO1XiFYEk2QJMgNsq4oNpllyYGUKuCoKsEGWf6orrJCJQQJ99BCACYeBjFXJ3w3AAAYACOGZj9D"
AZURE_SPEECH_REGION = "eastus"

# Configuración de WhatsApp API URL
WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"

# Directorios de archivos
UPLOAD_FOLDER = 'archivos_descargados'
ADJUNTOS_FOLDER = 'Adjuntos' 



#Campos de fechas
now = datetime.now()
fecha_actual = now.strftime('%Y-%m-%d %H:%M:%S')
format = now.strftime('%d_%m_%Y_%H_%M_%S')
 
# Log Status
log_status={
    "log1":["Ejecucion exitosa"],
    "log2":["Error SMTP"],
    "log3":["Error ejecucion"],
    "log4":["No se envia correo"],
    "log5":["Pendiente de Firmar"],
    "log6":["Documento Firmado"]    
}
 
##RUTA LOG
ruta_log= r"C:\Projects\WSP-python-webMeta_3\Log\log__reporte_novedades_"+format+".log"
 