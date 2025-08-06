
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
import time
import subprocess
import config
from datetime import datetime
import Funciones_py.crear_log as crear_log

# Configuración de Azure Speech-to-Text
AZURE_SPEECH_KEY = config.AZURE_SPEECH_KEY
AZURE_SPEECH_REGION = config.AZURE_SPEECH_REGION

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise ValueError("Azure Speech Key or Region is not set. Verifica tu archivo config.py.")

# Configuración global de Azure Speech
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.speech_recognition_language = "es-ES"

# Configuración del archivo de log para audio (se usará como fallback)
AUDIO_LOG_FILE = "logs/audio_processing.log"


def convertir_ogg_a_wav(input_file, output_file):
    """
    Convierte archivo OGG a WAV usando ffmpeg (equivalente al Node.js)
    Azure necesita WAV en 16 kHz, mono
    """
    try:
        # Log del inicio de conversión
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("AUDIO", f"Iniciando conversión OGG a WAV: {os.path.basename(input_file)}"))
        print(f"🔄 Convirtiendo OGG a WAV: {input_file} -> {output_file}")
        
        # Comando ffmpeg equivalente al Node.js
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-ar', '16000',  # 16 kHz requerido por Azure
            '-ac', '1',      # Mono
            '-f', 'wav',     # Formato WAV
            output_file
        ]
        
        # Ejecutar comando ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Log de conversión exitosa
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_exito(f"Conversión OGG a WAV exitosa", f"archivo: {os.path.basename(output_file)}"))
            print(f"✅ Conversión exitosa: {output_file}")
            return True
        else:
            # Log de error en conversión
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error(f"Error en conversión ffmpeg", f"archivo: {os.path.basename(input_file)}", result.stderr))
            print(f"❌ Error en conversión ffmpeg: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        # Log de timeout
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Timeout en conversión ffmpeg", f"archivo: {os.path.basename(input_file)}"))
        print("❌ Timeout en conversión ffmpeg")
        return False
    except Exception as e:
        # Log de error general
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error(f"Error al convertir OGG a WAV", f"archivo: {os.path.basename(input_file)}", e))
        print(f"❌ Error al convertir OGG a WAV: {e}")
        return False


def transcribir_audio_continuo(path):
    """
    Transcribe un archivo de audio WAV usando Azure Speech-to-Text con reconocimiento continuo
    Equivalente a transcribirAudioContinuo del Node.js
    """
    try:
        if not os.path.exists(path):
            # Log de archivo no encontrado
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Archivo de audio no encontrado", f"ruta: {path}"))
            raise FileNotFoundError(f"El archivo de audio no existe en la ruta: {path}")
        
        # Log del inicio de transcripción
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("TRANSCRIPTION", f"Iniciando transcripción con Azure: {os.path.basename(path)}"))
        print(f"🎤 Transcribiendo audio con Azure (reconocimiento continuo): {path}")
        
        # Configurar entrada de audio desde archivo WAV
        audio_config = speechsdk.audio.AudioConfig(filename=path)
        
        # Crear reconocedor de voz
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        # Variables para almacenar el resultado
        texto_completo = ""
        done = False
        error_occurred = False
        
        def recognizing_cb(evt):
            pass
        
        def recognized_cb(evt):
            nonlocal texto_completo
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                texto_completo += evt.result.text + " "
                # Log de texto reconocido
                crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("RECOGNITION", f"Texto reconocido: {evt.result.text[:50]}..."))
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                # Log de no reconocimiento
                crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("WARNING", "Speech could not be recognized"))
                print("NOMATCH: Speech could not be recognized.")
        
        def canceled_cb(evt):
            nonlocal done, error_occurred
            if evt.reason == speechsdk.CancellationReason.Error:
                error_occurred = True
                # Log de error crítico
                crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Transcripción cancelada por error crítico", f"archivo: {os.path.basename(path)}"))
                raise Exception("La transcripción fue cancelada debido a un error crítico.")
            else:
                done = True
        
        def session_stopped_cb(evt):
            nonlocal done
            done = True
        
        # Conectar eventos
        speech_recognizer.recognizing.connect(recognizing_cb)
        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.canceled.connect(canceled_cb)
        speech_recognizer.session_stopped.connect(session_stopped_cb)
        
        # Iniciar reconocimiento continuo
        speech_recognizer.start_continuous_recognition()
        
        # Esperar a que termine el reconocimiento
        while not done and not error_occurred:
            time.sleep(0.1)
        
        # Detener reconocimiento
        speech_recognizer.stop_continuous_recognition()
        
        if error_occurred:
            raise Exception("Error durante la transcripción")
        
        texto_final = texto_completo.strip()
        if texto_final:
            # Log de transcripción exitosa
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_exito(f"Transcripción exitosa", f"archivo: {os.path.basename(path)}, texto: {texto_final[:100]}..."))
            print(f"✅ Transcripción exitosa: {texto_final}")
            return texto_final
        else:
            # Log de transcripción fallida
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("No se pudo transcribir el audio", f"archivo: {os.path.basename(path)}"))
            print("❌ No se pudo transcribir el audio")
            return None
            
    except Exception as e:
        # Log de error en transcripción
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Error al transcribir con Azure", f"archivo: {os.path.basename(path)}", e))
        print(f"❌ Error al transcribir con Azure: {e}")
        return None


def limpiar_archivos_audio_temporales(audio_file_path, wav_file_path=None):
    """
    Limpia archivos de audio temporales después del procesamiento
    """
    try:
        # Log del inicio de limpieza
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("CLEANUP", "Iniciando limpieza de archivos temporales"))
        
        # Eliminar archivo WAV temporal si existe
        if wav_file_path and os.path.exists(wav_file_path):
            os.remove(wav_file_path)
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("CLEANUP", f"Archivo WAV temporal eliminado: {os.path.basename(wav_file_path)}"))
            print(f"🗑️ Archivo WAV temporal eliminado: {wav_file_path}")
        
        # Eliminar archivo de audio temporal original
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("CLEANUP", f"Archivo de audio temporal eliminado: {os.path.basename(audio_file_path)}"))
            print(f"🗑️ Archivo de audio temporal eliminado: {audio_file_path}")
        
        # Log de limpieza exitosa
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_exito("Limpieza de archivos temporales completada"))
        
    except Exception as e:
        # Log de error en limpieza
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Error al limpiar archivos temporales", "limpiar_archivos_audio_temporales", e))
        print(f"❌ Error al limpiar archivos temporales: {e}")


def procesar_audio_completo(audio_buffer, number):
    """
    Procesa un buffer de audio completo: guarda como OGG, convierte a WAV y transcribe
    Equivalente a handlerAI del Node.js
    """
    path_tmp_ogg = None
    path_tmp_wav = None
    
    try:
        # Log del inicio de procesamiento completo en archivo específico
        processing_msg = crear_log.crear_mensaje_log("PROCESSING", f"Iniciando procesamiento completo de audio para usuario: {number}")
        crear_log.escribir_log_sesion(number, processing_msg, "AUDIO")
        # También escribir en el log general
        crear_log.escribir(AUDIO_LOG_FILE, processing_msg)
        
        # Crear directorio tmp si no existe
        tmp_folder = 'tmp'
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)
            system_msg = crear_log.crear_mensaje_log("SYSTEM", f"Directorio temporal creado: {tmp_folder}")
            crear_log.escribir_log_sesion(number, system_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, system_msg)
            print(f"📁 Directorio temporal creado: {tmp_folder}")
        
        # Generar nombres de archivos temporales
        timestamp = int(time.time() * 1000)  # Equivalente a Date.now()
        path_tmp_ogg = os.path.join(tmp_folder, f"voice-note-{timestamp}.ogg")
        path_tmp_wav = os.path.join(tmp_folder, f"voice-note-{timestamp}.wav")
        
        # Guardar archivo OGG
        with open(path_tmp_ogg, 'wb') as f:
            f.write(audio_buffer)
        success_msg = crear_log.log_exito(f"Archivo OGG guardado", f"archivo: {os.path.basename(path_tmp_ogg)}, usuario: {number}")
        crear_log.escribir_log_sesion(number, success_msg, "AUDIO")
        # También escribir en el log general
        crear_log.escribir(AUDIO_LOG_FILE, success_msg)
        print(f"✅ Archivo OGG guardado: {path_tmp_ogg}")
        
        # Convertir a WAV
        if not convertir_ogg_a_wav(path_tmp_ogg, path_tmp_wav):
            raise Exception("Error en conversión OGG a WAV")
        
        # Transcribir audio
        texto_transcrito = transcribir_audio_continuo(path_tmp_wav)
        
        # Log del resultado final en archivo específico
        if texto_transcrito:
            final_success_msg = crear_log.log_exito(f"Procesamiento completo exitoso", f"usuario: {number}, texto: {texto_transcrito[:100]}...")
            crear_log.escribir_log_sesion(number, final_success_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, final_success_msg)
        else:
            final_error_msg = crear_log.log_error("Procesamiento completo fallido", f"usuario: {number}")
            crear_log.escribir_log_sesion(number, final_error_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, final_error_msg)
        
        return texto_transcrito
        
    except Exception as e:
        # Log de error en procesamiento completo en archivo específico
        error_msg = crear_log.log_error("Error al procesar audio completo", f"usuario: {number}", e)
        crear_log.escribir_log_sesion(number, error_msg, "AUDIO")
        # También escribir en el log general
        crear_log.escribir(AUDIO_LOG_FILE, error_msg)
        print(f"❌ Error al procesar audio completo: {e}")
        return None
        
    finally:
        # Eliminar archivos temporales
        try:
            if path_tmp_ogg and os.path.exists(path_tmp_ogg):
                os.remove(path_tmp_ogg)
                cleanup_msg = crear_log.crear_mensaje_log("CLEANUP", f"Archivo OGG temporal eliminado: {os.path.basename(path_tmp_ogg)}")
                crear_log.escribir_log_sesion(number, cleanup_msg, "AUDIO")
                # También escribir en el log general
                crear_log.escribir(AUDIO_LOG_FILE, cleanup_msg)
                print(f"🗑️ Archivo OGG temporal eliminado: {path_tmp_ogg}")
        except Exception as e:
            cleanup_error_msg = crear_log.log_error("Error al eliminar archivo OGG", f"archivo: {os.path.basename(path_tmp_ogg) if path_tmp_ogg else 'N/A'}", e)
            crear_log.escribir_log_sesion(number, cleanup_error_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, cleanup_error_msg)
            print(f"⚠️ Error al eliminar archivo OGG: {e}")
            
        try:
            if path_tmp_wav and os.path.exists(path_tmp_wav):
                os.remove(path_tmp_wav)
                cleanup_msg = crear_log.crear_mensaje_log("CLEANUP", f"Archivo WAV temporal eliminado: {os.path.basename(path_tmp_wav)}")
                crear_log.escribir_log_sesion(number, cleanup_msg, "AUDIO")
                # También escribir en el log general
                crear_log.escribir(AUDIO_LOG_FILE, cleanup_msg)
                print(f"🗑️ Archivo WAV temporal eliminado: {path_tmp_wav}")
        except Exception as e:
            cleanup_error_msg = crear_log.log_error("Error al eliminar archivo WAV", f"archivo: {os.path.basename(path_tmp_wav) if path_tmp_wav else 'N/A'}", e)
            crear_log.escribir_log_sesion(number, cleanup_error_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, cleanup_error_msg)
            print(f"⚠️ Error al eliminar archivo WAV: {e}")


def procesar_audio_desde_url(media_url, number, whatsapp_token):
    """
    Descarga audio desde URL de WhatsApp y lo procesa
    """
    try:
        import requests
        
        # Log del inicio de descarga en archivo específico
        download_msg = crear_log.crear_mensaje_log("DOWNLOAD", f"Iniciando descarga de audio desde URL para usuario: {number}")
        crear_log.escribir_log_sesion(number, download_msg, "AUDIO")
        # También escribir en el log general
        crear_log.escribir(AUDIO_LOG_FILE, download_msg)
        print(f"📥 Descargando audio desde URL: {media_url}")
        
        # Descargar archivo con headers de autorización
        headers = {
            "Authorization": f"Bearer {whatsapp_token}"
        }
        
        response = requests.get(media_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            # Obtener el buffer de audio
            audio_buffer = response.content
            
            # Log de descarga exitosa en archivo específico
            download_success_msg = crear_log.log_exito(f"Audio descargado exitosamente", f"usuario: {number}, tamaño: {len(audio_buffer)} bytes")
            crear_log.escribir_log_sesion(number, download_success_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, download_success_msg)
            
            # Procesar el audio completo
            texto_transcrito = procesar_audio_completo(audio_buffer, number)
            
            return texto_transcrito
        else:
            # Log de error en descarga en archivo específico
            download_error_msg = crear_log.log_error(f"Error al descargar audio", f"usuario: {number}, status: {response.status_code}")
            crear_log.escribir_log_sesion(number, download_error_msg, "AUDIO")
            # También escribir en el log general
            crear_log.escribir(AUDIO_LOG_FILE, download_error_msg)
            print(f"❌ Error al descargar audio: {response.status_code}")
            return None
            
    except Exception as e:
        # Log de error general en archivo específico
        general_error_msg = crear_log.log_error("Error al procesar audio desde URL", f"usuario: {number}", e)
        crear_log.escribir_log_sesion(number, general_error_msg, "AUDIO")
        # También escribir en el log general
        crear_log.escribir(AUDIO_LOG_FILE, general_error_msg)
        print(f"❌ Error al procesar audio desde URL: {e}")
        return None


def convertir_audio_a_wav(audio_file_path):
    """
    Función de compatibilidad - convierte cualquier formato a WAV usando ffmpeg
    """
    try:
        # Log del inicio de conversión de compatibilidad
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("COMPATIBILITY", f"Conversión de compatibilidad: {os.path.basename(audio_file_path)}"))
        print(f"🔄 Convirtiendo audio a WAV: {audio_file_path}")
        
        # Crear directorio audios_tmp si no existe
        audios_tmp_folder = 'audios_tmp'
        if not os.path.exists(audios_tmp_folder):
            os.makedirs(audios_tmp_folder)
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("SYSTEM", f"Directorio temporal creado: {audios_tmp_folder}"))
            print(f"📁 Directorio temporal creado: {audios_tmp_folder}")
        
        # Crear archivo temporal para el WAV
        wav_filename = f"temp_{os.path.basename(audio_file_path).rsplit('.', 1)[0]}.wav"
        wav_file_path = os.path.join(audios_tmp_folder, wav_filename)
        
        # Usar ffmpeg para conversión
        if convertir_ogg_a_wav(audio_file_path, wav_file_path):
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_exito(f"Conversión de compatibilidad exitosa", f"archivo: {os.path.basename(wav_file_path)}"))
            return wav_file_path
        else:
            crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Conversión de compatibilidad fallida", f"archivo: {os.path.basename(audio_file_path)}"))
            return None
            
    except Exception as e:
        crear_log.escribir(AUDIO_LOG_FILE, crear_log.log_error("Error en conversión de compatibilidad", f"archivo: {os.path.basename(audio_file_path)}", e))
        print(f"❌ Error al convertir audio a WAV: {e}")
        return None

def transcribir_audio_con_azure(wav_file_path):
    """
    Función de compatibilidad - transcribe archivo WAV usando reconocimiento continuo
    """
    # Log de transcripción de compatibilidad
    crear_log.escribir(AUDIO_LOG_FILE, crear_log.crear_mensaje_log("COMPATIBILITY", f"Transcripción de compatibilidad: {os.path.basename(wav_file_path)}"))
    return transcribir_audio_continuo(wav_file_path)