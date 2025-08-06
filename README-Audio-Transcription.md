# Funcionalidad de Transcripción de Audio con Azure Speech-to-Text

## Descripción

Esta funcionalidad permite procesar archivos de audio (incluyendo notas de voz) enviados por WhatsApp, convertirlos a formato WAV y transcribirlos usando Azure Speech-to-Text. El usuario puede validar la transcripción antes de continuar con el reporte.

## Características

- ✅ Conversión automática de audio a formato WAV (16kHz, mono, 16-bit)
- ✅ Transcripción usando Azure Speech-to-Text
- ✅ Validación de transcripción por parte del usuario
- ✅ Soporte para archivos de audio y notas de voz
- ✅ Limpieza automática de archivos temporales
- ✅ Manejo de errores y reintentos

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` basado en `env.example`:

```bash
cp env.example .env
```

Edita el archivo `.env` y configura las siguientes variables:

```env
# Variables de entorno para WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=tu_token_de_whatsapp_aqui

# Variables de entorno para Azure Speech-to-Text
AZURE_SPEECH_KEY=tu_clave_de_azure_speech_aqui
AZURE_SPEECH_REGION=tu_region_de_azure_aqui
```

### 3. Configurar Azure Speech-to-Text

1. Ve al [Portal de Azure](https://portal.azure.com)
2. Crea un recurso de "Speech Service"
3. Obtén la clave de suscripción y la región
4. Configura las variables de entorno con estos valores

## Flujo de Funcionamiento

### 1. Recepción de Audio
- El usuario envía un archivo de audio o nota de voz
- El sistema descarga el archivo y lo guarda en `archivos_descargados/`

### 2. Conversión a WAV
- El archivo se convierte automáticamente a formato WAV
- Configuración: 16kHz, mono, 16-bit (óptimo para Azure)

### 3. Transcripción con Azure
- El archivo WAV se envía a Azure Speech-to-Text
- Se configura para reconocimiento en español (es-ES)
- Se obtiene el texto transcrito

### 4. Validación del Usuario
- Se muestra la transcripción al usuario
- Se presentan dos opciones:
  - "Si estoy de acuerdo"
  - "No, deseo volver a enviarla"

### 5. Continuación del Flujo
- Si el usuario confirma: se usa el texto transcrito y se continúa
- Si el usuario rechaza: se solicita un nuevo audio

## Archivos Modificados

### `app.py`
- Agregadas funciones de conversión de audio
- Integración con Azure Speech-to-Text
- Manejo de validación de transcripción
- Limpieza de archivos temporales

### `util.py`
- Nueva función `ListValidacionTranscripcion()` para mostrar opciones de validación

### `requirements.txt`
- Agregadas dependencias:
  - `azure-cognitiveservices-speech==1.37.0`
  - `pydub==0.25.1`

## Funciones Principales

### `convertir_audio_a_wav(audio_file_path)`
Convierte cualquier formato de audio a WAV usando pydub.

### `transcribir_audio_con_azure(wav_file_path)`
Transcribe el archivo WAV usando Azure Speech-to-Text.

### `procesar_audio_completo(audio_file_path, number)`
Procesa el archivo completo: conversión + transcripción.

### `mostrar_transcripcion_y_validar(number, texto_transcrito)`
Muestra la transcripción al usuario y solicita validación.

### `limpiar_archivos_audio_temporales(audio_file_path, wav_file_path)`
Limpia archivos temporales después del procesamiento.

## Manejo de Errores

- Si falla la conversión de audio: mensaje de error al usuario
- Si falla la transcripción: solicitud de nuevo audio
- Si no están configuradas las variables de Azure: mensaje de error en logs
- Si el usuario no responde correctamente: solicitud de respuesta válida

## Configuración de Azure

### Requisitos
- Cuenta de Azure activa
- Recurso de Speech Service creado
- Clave de suscripción válida
- Región configurada

### Configuración de Idioma
El sistema está configurado para español (es-ES). Para cambiar el idioma, modifica la línea:

```python
speech_config.speech_recognition_language = "es-ES"
```

## Notas Importantes

1. **Archivos Temporales**: Los archivos WAV se crean temporalmente y se eliminan después del procesamiento
2. **Tamaño de Archivo**: Azure tiene límites de tamaño para archivos de audio
3. **Calidad de Audio**: Para mejores resultados, el audio debe ser claro y sin ruido
4. **Conexión a Internet**: Se requiere conexión a internet para usar Azure Speech-to-Text

## Troubleshooting

### Error: "Variables de entorno no configuradas"
- Verifica que `AZURE_SPEECH_KEY` y `AZURE_SPEECH_REGION` estén configuradas
- Asegúrate de que el archivo `.env` esté en el directorio raíz

### Error: "No se pudo reconocer el audio"
- Verifica que el audio sea claro y sin ruido
- Asegúrate de que el archivo no esté corrupto
- Intenta con un audio más corto

### Error: "Error al convertir audio a WAV"
- Verifica que pydub esté instalado correctamente
- Asegúrate de que el archivo de audio sea válido
- Verifica los permisos de escritura en el directorio

## Soporte

Para problemas o preguntas sobre esta funcionalidad, revisa:
1. Los logs del sistema para mensajes de error
2. La configuración de Azure Speech Service
3. Las variables de entorno
4. La calidad del audio enviado 