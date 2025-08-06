# Configuración del Proyecto WhatsApp WebMeta

## Cambios Realizados

Se ha migrado el sistema de configuración de variables de entorno desde archivos `.env` a un archivo Python centralizado `config.py` para mejorar la gestión y mantenimiento de las configuraciones del proyecto.

## Archivo de Configuración

### `config.py`

Este archivo centraliza todas las variables de configuración del proyecto. Debes editar este archivo con tus valores reales:

```python
# Configuración de WhatsApp Business API
WHATSAPP_ACCESS_TOKEN = "tu_token_de_whatsapp_aqui"
WHATSAPP_PHONE_ID = "tu_phone_number_id_aqui"
VERIFY_TOKEN = "mi_token_secreto_para_webhook"

# Configuración del servidor
PORT = 3000

# Configuración de base de datos
DB_DRIVER = "ODBC Driver 17 for SQL Server"
DB_SERVER = "tu_servidor_sql_aqui"
DB_DATABASE = "tu_base_de_datos_aqui"
DB_USER = "tu_usuario_aqui"
DB_PASSWORD = "tu_contraseña_aqui"
DB_TRUSTED_CONNECTION = "yes"

# Configuración de Azure Speech-to-Text
AZURE_SPEECH_KEY = "tu_azure_speech_key_aqui"
AZURE_SPEECH_REGION = "tu_azure_region_aqui"

# Configuración de WhatsApp API URL
WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"

# Directorios de archivos
UPLOAD_FOLDER = 'archivos_descargados'
ADJUNTOS_FOLDER = 'Adjuntos'
```

## Configuración Requerida

### 1. WhatsApp Business API
- `WHATSAPP_ACCESS_TOKEN`: Token de acceso de WhatsApp Business API
- `WHATSAPP_PHONE_ID`: ID del número de teléfono de WhatsApp Business
- `VERIFY_TOKEN`: Token secreto para verificar webhooks

### 2. Base de Datos SQL Server
- `DB_DRIVER`: Driver ODBC para SQL Server
- `DB_SERVER`: Servidor de base de datos
- `DB_DATABASE`: Nombre de la base de datos
- `DB_USER`: Usuario de la base de datos
- `DB_PASSWORD`: Contraseña de la base de datos
- `DB_TRUSTED_CONNECTION`: Configuración de conexión confiable

### 3. Azure Speech-to-Text
- `AZURE_SPEECH_KEY`: Clave de suscripción de Azure Speech
- `AZURE_SPEECH_REGION`: Región de Azure Speech

### 4. Configuración del Servidor
- `PORT`: Puerto en el que se ejecutará la aplicación

## Archivos Modificados

Los siguientes archivos han sido actualizados para usar el nuevo sistema de configuración:

### Archivos Principales
- `app.py` - Archivo principal de la aplicación Flask
- `config.py` - Nuevo archivo de configuración centralizada

### Funciones de Base de Datos (`Funciones_bd/`)
- `buscar_usuario.py`
- `buscar_idnovedad.py`
- `insertar_incidente.py`
- `insertar_bd_azure.py`

### Funciones de Procesamiento (`Funciones_py/`)
- `archivos_adjuntos.py`
- `procesar_audio.py`

## Ventajas del Nuevo Sistema

1. **Centralización**: Todas las configuraciones están en un solo lugar
2. **Facilidad de mantenimiento**: Cambios de configuración en un solo archivo
3. **Mejor control de versiones**: El archivo `config.py` puede ser incluido en el control de versiones
4. **Eliminación de dependencias**: No se requiere la librería `python-dotenv`
5. **Mejor organización**: Configuraciones agrupadas por categorías

## Instrucciones de Uso

1. **Editar configuración**: Modifica el archivo `config.py` con tus valores reales
2. **Verificar configuración**: Asegúrate de que todas las variables tengan valores válidos
3. **Ejecutar aplicación**: La aplicación ahora usará automáticamente las configuraciones del archivo `config.py`

## Migración desde .env

Si tenías un archivo `.env`, puedes migrar las variables de la siguiente manera:

```bash
# Antes (.env)
WHATSAPP_ACCESS_TOKEN=tu_token_aqui
DB_SERVER=tu_servidor_aqui

# Ahora (config.py)
WHATSAPP_ACCESS_TOKEN = "tu_token_aqui"
DB_SERVER = "tu_servidor_aqui"
```

## Notas Importantes

- **Seguridad**: Asegúrate de no compartir el archivo `config.py` con información sensible en repositorios públicos
- **Backup**: Mantén una copia de seguridad de tu configuración
- **Validación**: El sistema validará que las configuraciones críticas estén presentes al iniciar

## Solución de Problemas

Si encuentras errores relacionados con configuraciones:

1. Verifica que todas las variables en `config.py` tengan valores válidos
2. Asegúrate de que el archivo `config.py` esté en el directorio raíz del proyecto
3. Verifica que los imports de `config` estén correctos en todos los archivos 