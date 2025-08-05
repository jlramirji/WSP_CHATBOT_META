from flask import Flask, request, jsonify
import requests
import os
from Funciones_bd.buscar_idnovedad import buscar_idnovedad
from Funciones_py import leer_archivos
from Funciones_py.procesar_audio import convertir_audio_a_wav, transcribir_audio_con_azure
from datetime import datetime, timedelta
import whatsappservice
import util
import time
import mimetypes
import config

# Configuración de WhatsApp API
WHATSAPP_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_API_URL = config.WHATSAPP_API_URL

# Eliminamos la importación circular
# from app import UPLOAD_FOLDER,user_sessions

def generar_nombre_archivo_unico(base_name, extension, upload_folder):
    """
    Genera un nombre de archivo único con timestamp de microsegundos
    """
    import time
    unique_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Incluye milisegundos
    filename = f"{base_name}_{unique_timestamp}{extension}"
    
    # Verificar si el archivo ya existe y agregar un sufijo si es necesario
    base_filepath = os.path.join(upload_folder, filename)
    counter = 1
    while os.path.exists(base_filepath):
        name_without_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        filename = f"{name_without_ext}_{counter}{ext}"
        base_filepath = os.path.join(upload_folder, filename)
        counter += 1
    
    return filename

def enviar_mensajes_con_espera(mensajes, number, espera=3):
    ###Envía una lista de mensajes por WhatsApp con un tiempo de espera entre cada uno.
    for mensaje in mensajes:
        whatsappservice.SendMessageWhatsApp(
            util.TextMessage(mensaje, number)
        )
        time.sleep(espera)


def obtener_media_url(media_id):
    """
    Obtiene la URL de descarga de un archivo de WhatsApp usando su media_id
    """
    try:
        url = f"{WHATSAPP_API_URL}/{media_id}"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('url')
        else:
            print(f"❌ Error al obtener URL de media: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error al obtener media URL: {e}")
        return None

# def obtener_media_url(media_id):
#     """
#     Obtiene la URL de descarga de un archivo de WhatsApp usando su media_id
#     """
#     try:
#         # Verificar que el token esté disponible
#         if not WHATSAPP_TOKEN:
#             print("❌ Error: WHATSAPP_TOKEN no está configurado")
#             return None
            
#         url = f"{WHATSAPP_API_URL}/{media_id}"
#         headers = {
#             "Authorization": f"Bearer {WHATSAPP_TOKEN}"
#         }
        
#         print(f"🔍 Intentando obtener URL para media_id: {media_id}")
#         print(f"🔍 URL de la API: {url}")
#         print(f"🔍 Token configurado: {'Sí' if WHATSAPP_TOKEN else 'No'}")
        
#         response = requests.get(url, headers=headers)
        
#         print(f"🔍 Respuesta de la API: {response.status_code}")
        
#         if response.status_code == 200:
#             data = response.json()
#             media_url = data.get('url')
#             print(f"✅ URL obtenida exitosamente: {media_url[:50]}..." if media_url else "❌ No se encontró URL en la respuesta")
#             return media_url
#         else:
#             print(f"❌ Error al obtener URL de media: {response.status_code}")
#             print(f"❌ Respuesta del servidor: {response.text}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al obtener media URL: {e}")
#         return None

def descargar_archivo(media_url, filename, upload_folder):
    """
    Descarga un archivo desde una URL y lo guarda localmente
    """
    try:
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        response = requests.get(media_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            filepath = os.path.join(upload_folder, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Archivo descargado: {filepath}")
            return filepath
        else:
            print(f"❌ Error al descargar archivo: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error al descargar archivo: {e}")
        return None

def descargar_archivo_temporal(media_url, filename):
    """
    Descarga un archivo desde una URL y lo guarda temporalmente en la carpeta audios_tmp
    """
    try:
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        response = requests.get(media_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            # Crear directorio audios_tmp si no existe
            audios_tmp_folder = 'audios_tmp'
            if not os.path.exists(audios_tmp_folder):
                os.makedirs(audios_tmp_folder)
                print(f"📁 Directorio temporal creado: {audios_tmp_folder}")
            
            # Crear archivo temporal en la carpeta audios_tmp
            temp_filepath = os.path.join(audios_tmp_folder, filename)
            
            with open(temp_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Archivo temporal descargado: {temp_filepath}")
            return temp_filepath
        else:
            print(f"❌ Error al descargar archivo: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error al descargar archivo temporal: {e}")
        return None

def procesar_archivo_adjunto(message, number, upload_folder, user_sessions):
    """
    Procesa y descarga archivos adjuntos (audio, imagen, video, documento)
    """
    try:
        message_type = message.get('type', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Enviar mensaje de procesamiento para archivos de audio
        if message_type in ['audio', 'voice']:
            whatsappservice.SendMessageWhatsApp(
                util.TextMessage("🔄 Procesando nota de voz...", number)
            )
        
        if message_type == 'audio':
            return procesar_audio(message, number, timestamp, user_sessions)
        elif message_type == 'image':
            return procesar_imagen(message, number, timestamp, upload_folder, user_sessions)
        elif message_type == 'video':
            return procesar_video(message, number, timestamp, upload_folder, user_sessions)
        elif message_type == 'document':
            return procesar_documento(message, number, timestamp, upload_folder, user_sessions)
        elif message_type == 'voice':
            return procesar_nota_voz(message, number, timestamp, user_sessions)
        else:
            print(f"⚠️ Tipo de archivo no soportado: {message_type}")
            return None
            
    except Exception as e:
        print(f"❌ Error al procesar archivo adjunto: {e}")
        return None

def procesar_audio(message, number, timestamp, user_sessions):
    """
    Procesa archivos de audio y los transcribe con Azure usando archivos temporales
    """
    try:
        audio_data = message.get('audio', {})
        media_id = audio_data.get('id')
        
        if not media_id:
            print("❌ No se encontró media_id en el audio")
            return None
        
        # Obtener URL de descarga
        media_url = obtener_media_url(media_id)
        if not media_url:
            return None
        
        # Generar nombre de archivo único
        filename = generar_nombre_archivo_unico(f"audio_{number}", ".mp3", "audios_tmp")
        
        # Descargar archivo temporalmente
        temp_filepath = descargar_archivo_temporal(media_url, filename)
        
        if temp_filepath:
            print(f"🎵 Audio temporal descargado para {number}: {temp_filepath}")
            
            # Procesar audio completo (convertir a WAV y transcribir)
            texto_transcrito = procesar_audio_completo(temp_filepath, number, user_sessions)
            
            if texto_transcrito:
                # Mostrar transcripción al usuario para validación
                mostrar_transcripcion_y_validar(number, texto_transcrito)
            else:
                # Si falla la transcripción, enviar mensaje de error
                whatsappservice.SendMessageWhatsApp(
                    util.TextMessage("❌ No se pudo transcribir el audio. Por favor, intenta enviar una nota de voz más clara o escribe tu mensaje.", number)
                )
            
            return temp_filepath
        
        return None
        
    except Exception as e:
        print(f"❌ Error al procesar audio: {e}")
        return None

def procesar_imagen(message, number, timestamp, upload_folder, user_sessions):
    """
    Procesa archivos de imagen
    """
    try:
        image_data = message.get('image', {})
        media_id = image_data.get('id')
        
        if not media_id:
            print("❌ No se encontró media_id en la imagen")
            return None
        
        # Obtener URL de descarga
        media_url = obtener_media_url(media_id)
        if not media_url:
            return None
        
        # Determinar extensión basada en mimetype
        mimetype = image_data.get('mime_type', 'image/jpeg')
        extension = mimetypes.guess_extension(mimetype) or '.jpg'
        
        # Generar nombre de archivo único
        filename = generar_nombre_archivo_unico(f"imagen_{number}", extension, upload_folder)
        print(f"📸 Generando nombre único para imagen: {filename}")
        
        # Descargar archivo
        filepath = descargar_archivo(media_url, filename, upload_folder)
        
        if filepath:
            # Guardar información en la sesión del usuario
            if number in user_sessions:
                # Inicializar lista si no existe
                if 'imagenes_descargadas' not in user_sessions[number]:
                    user_sessions[number]['imagenes_descargadas'] = []
                
                # Agregar archivo a la lista
                user_sessions[number]['imagenes_descargadas'].append(filepath)
                user_sessions[number]['tipo_archivo'] = 'imagen'
                
                # Mantener compatibilidad con el código existente (último archivo)
                user_sessions[number]['imagen_descargada'] = filepath
            
            print(f"🖼️ Imagen procesada para {number}: {filepath}")
            return filepath
        
        return None
        
    except Exception as e:
        print(f"❌ Error al procesar imagen: {e}")
        return None

def procesar_video(message, number, timestamp, upload_folder, user_sessions):
    """
    Procesa archivos de video
    """
    try:
        video_data = message.get('video', {})
        media_id = video_data.get('id')
        
        if not media_id:
            print("❌ No se encontró media_id en el video")
            return None
        
        # Obtener URL de descarga
        media_url = obtener_media_url(media_id)
        if not media_url:
            return None
        
        # Determinar extensión basada en mimetype
        mimetype = video_data.get('mime_type', 'video/mp4')
        extension = mimetypes.guess_extension(mimetype) or '.mp4'
        
        # Generar nombre de archivo único
        filename = generar_nombre_archivo_unico(f"video_{number}", extension, upload_folder)
        
        # Descargar archivo
        filepath = descargar_archivo(media_url, filename, upload_folder)
        
        if filepath:
            # Guardar información en la sesión del usuario
            if number in user_sessions:
                # Inicializar lista si no existe
                if 'videos_descargados' not in user_sessions[number]:
                    user_sessions[number]['videos_descargados'] = []
                
                # Agregar archivo a la lista
                user_sessions[number]['videos_descargados'].append(filepath)
                user_sessions[number]['tipo_archivo'] = 'video'
                
                # Mantener compatibilidad con el código existente (último archivo)
                user_sessions[number]['video_descargado'] = filepath
            
            print(f"🎥 Video procesado para {number}: {filepath}")
            return filepath
        
        return None
        
    except Exception as e:
        print(f"❌ Error al procesar video: {e}")
        return None

def procesar_documento(message, number, timestamp, upload_folder, user_sessions):
    """
    Procesa archivos de documento
    """
    try:
        document_data = message.get('document', {})
        media_id = document_data.get('id')
        
        if not media_id:
            print("❌ No se encontró media_id en el documento")
            return None
        
        # Obtener URL de descarga
        media_url = obtener_media_url(media_id)
        if not media_url:
            return None
        
        # Obtener nombre original del archivo
        original_filename = document_data.get('filename', 'documento')
        
        # Determinar extensión
        mimetype = document_data.get('mime_type', 'application/octet-stream')
        extension = mimetypes.guess_extension(mimetype) or '.bin'
        
        # Generar nombre de archivo único
        filename = generar_nombre_archivo_unico(f"doc_{number}_{original_filename}", extension, upload_folder)
        
        # Descargar archivo
        filepath = descargar_archivo(media_url, filename, upload_folder)
        
        if filepath:
            # Guardar información en la sesión del usuario
            if number in user_sessions:
                # Inicializar lista si no existe
                if 'documentos_descargados' not in user_sessions[number]:
                    user_sessions[number]['documentos_descargados'] = []
                
                # Agregar archivo a la lista
                user_sessions[number]['documentos_descargados'].append(filepath)
                user_sessions[number]['tipo_archivo'] = 'documento'
                
                # Mantener compatibilidad con el código existente (último archivo)
                user_sessions[number]['documento_descargado'] = filepath
            
            print(f"📄 Documento procesado para {number}: {filepath}")
            return filepath
        
        return None
        
    except Exception as e:
        print(f"❌ Error al procesar documento: {e}")
        return None

def procesar_nota_voz(message, number, timestamp, user_sessions):
    """
    Procesa notas de voz (voice messages) y las transcribe con Azure usando archivos temporales
    """
    try:
        voice_data = message.get('voice', {})
        media_id = voice_data.get('id')
        
        if not media_id:
            print("❌ No se encontró media_id en la nota de voz")
            return None
        
        # Obtener URL de descarga
        media_url = obtener_media_url(media_id)
        if not media_url:
            return None
        
        # Generar nombre de archivo único
        filename = generar_nombre_archivo_unico(f"nota_voz_{number}", ".ogg", "audios_tmp")
        
        # Descargar archivo temporalmente
        temp_filepath = descargar_archivo_temporal(media_url, filename)
        
        if temp_filepath:
            print(f"🎤 Nota de voz temporal descargada para {number}: {temp_filepath}")
            
            # Procesar audio completo (convertir a WAV y transcribir)
            texto_transcrito = procesar_audio_completo(temp_filepath, number, user_sessions)
            
            if texto_transcrito:
                # Mostrar transcripción al usuario para validación
                mostrar_transcripcion_y_validar(number, texto_transcrito)
            else:
                # Si falla la transcripción, enviar mensaje de error
                whatsappservice.SendMessageWhatsApp(
                    util.TextMessage("❌ No se pudo transcribir la nota de voz. Por favor, intenta enviar una nota más clara o escribe tu mensaje.", number)
                )
            
            return temp_filepath
        
        return None
        
    except Exception as e:
        print(f"❌ Error al procesar nota de voz: {e}")
        return None

def obtener_info_archivo(filepath):
    """
    Obtiene información del archivo descargado
    """
    try:
        if not filepath or not os.path.exists(filepath):
            return None
        
        stat = os.stat(filepath)
        return {
            'ruta': filepath,
            'tamaño_bytes': stat.st_size,
            'tamaño_mb': round(stat.st_size / (1024 * 1024), 2),
            'fecha_creacion': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'extension': os.path.splitext(filepath)[1]
        }
        
    except Exception as e:
        print(f"❌ Error al obtener info del archivo: {e}")
        return None
    
def procesar_audio_completo(audio_file_path, number, user_sessions):
    """
    Procesa un archivo de audio completo: convierte a WAV y transcribe con Azure
    Limpia automáticamente los archivos temporales después del procesamiento
    """
    wav_file_path = None
    try:
        # Convertir a WAV
        wav_file_path = convertir_audio_a_wav(audio_file_path)
        if not wav_file_path:
            return None
        
        # Transcribir con Azure
        texto_transcrito = transcribir_audio_con_azure(wav_file_path)
        if not texto_transcrito:
            return None
        
        # Guardar información en la sesión del usuario
        if number in user_sessions:
            user_sessions[number]['texto_transcrito'] = texto_transcrito
            user_sessions[number]['esperando'] = 'validar_transcripcion'
        
        return texto_transcrito
        
    except Exception as e:
        print(f"❌ Error en procesamiento completo de audio: {e}")
        return None
    finally:
        # Limpiar archivos temporales automáticamente
        limpiar_archivos_audio_temporales(audio_file_path, wav_file_path)

def limpiar_archivos_audio_temporales(audio_file_path, wav_file_path=None):
    """
    Limpia archivos de audio temporales después del procesamiento
    """
    try:
        # Eliminar archivo WAV temporal si existe
        if wav_file_path and os.path.exists(wav_file_path):
            os.remove(wav_file_path)
            print(f"🗑️ Archivo WAV temporal eliminado: {wav_file_path}")
        
        # Eliminar archivo de audio temporal original
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            print(f"🗑️ Archivo de audio temporal eliminado: {audio_file_path}")
        
    except Exception as e:
        print(f"❌ Error al limpiar archivos temporales: {e}")


def mostrar_transcripcion_y_validar(number, texto_transcrito):
    """
    Muestra la transcripción al usuario y solicita validación
    """
    
    try:
        # PRIMERO: Mostrar la transcripción
        mensaje = [
            f"🎤 *Transcripción del audio:*\n\n{texto_transcrito}"
        ]
        enviar_mensajes_con_espera(mensaje, number, espera=2)
       
        # # Enviar opciones de validación
        # whatsappservice.SendMessageWhatsApp(
        #     util.ListValTranscr(number)
        # )   
        whatsappservice.SendMessageWhatsApp(
            util.ButtonsValTranscr(number)
        )        
        
        print(f"✅ Transcripción enviada para validación a {number}")
        
    except Exception as e:
        print(f"❌ Error al mostrar transcripción: {e}")
