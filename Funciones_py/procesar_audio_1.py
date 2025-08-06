
# import azure.cognitiveservices.speech as speechsdk
# from pydub import AudioSegment
# from pydub.silence import detect_nonsilent
# import os
# import asyncio
# import config

# # Configuración de Azure Speech-to-Text
# AZURE_SPEECH_KEY = config.AZURE_SPEECH_KEY
# AZURE_SPEECH_REGION = config.AZURE_SPEECH_REGION

# if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
#     raise ValueError("Azure Speech Key or Region is not set. Verifica tu archivo config.py.")

# # Configuración global de Azure Speech
# speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
# speech_config.speech_recognition_language = "es-ES"


# def convertir_audio_a_wav(audio_file_path):
#     """
#     Convierte un archivo de audio a formato WAV usando pydub
#     Guarda el archivo WAV temporal en la carpeta audios_tmp
#     """
#     try:
#         print(f"🔄 Convirtiendo audio a WAV: {audio_file_path}")
        
#         # Cargar el archivo de audio
#         audio = AudioSegment.from_file(audio_file_path)
        
#         # Crear directorio audios_tmp si no existe
#         audios_tmp_folder = 'audios_tmp'
#         if not os.path.exists(audios_tmp_folder):
#             os.makedirs(audios_tmp_folder)
#             print(f"📁 Directorio temporal creado: {audios_tmp_folder}")
        
#         # Crear archivo temporal para el WAV en la carpeta audios_tmp
#         wav_filename = f"temp_{os.path.basename(audio_file_path).rsplit('.', 1)[0]}.wav"
#         wav_file_path = os.path.join(audios_tmp_folder, wav_filename)
        
#         # Exportar como WAV (16kHz, mono, 16-bit)
#         audio = audio.set_frame_rate(16000).set_channels(1)
#         audio.export(wav_file_path, format='wav')
        
#         print(f"✅ Audio convertido a WAV temporal: {wav_file_path}")
#         return wav_file_path
        
#     except Exception as e:
#         print(f"❌ Error al convertir audio a WAV: {e}")
#         return None

# def transcribir_audio_con_azure(wav_file_path):
#     """
#     Transcribe un archivo de audio WAV usando Azure Speech-to-Text con reconocimiento continuo
#     """
#     try:
#         if not os.path.exists(wav_file_path):
#             raise FileNotFoundError(f"El archivo de audio no existe en la ruta: {wav_file_path}")
        
#         print(f"🎤 Transcribiendo audio con Azure (reconocimiento continuo): {wav_file_path}")
        
#         # Configurar entrada de audio desde archivo
#         audio_config = speechsdk.audio.AudioConfig(filename=wav_file_path)
        
#         # Crear reconocedor de voz
#         speech_recognizer = speechsdk.SpeechRecognizer(
#             speech_config=speech_config, 
#             audio_config=audio_config
#         )
        
#         # Variables para almacenar el resultado
#         texto_completo = ""
#         done = False
        
#         def recognizing_cb(evt):
#             # print(f"RECOGNIZING: Text={evt.result.text}")
#             pass
        
#         def recognized_cb(evt):
#             nonlocal texto_completo
#             if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
#                 # print(f"RECOGNIZED: Text={evt.result.text}")
#                 texto_completo += evt.result.text + " "
#             elif evt.result.reason == speechsdk.ResultReason.NoMatch:
#                 print("NOMATCH: Speech could not be recognized.")
        
#         def canceled_cb(evt):
#             nonlocal done
#             # print(f"CANCELED: Reason={evt.reason}")
#             if evt.reason == speechsdk.CancellationReason.Error:
#                 # print(f"CANCELED: ErrorCode={evt.error_code}")
#                 # print(f"CANCELED: ErrorDetails={evt.error_details}")
#                 raise Exception("La transcripción fue cancelada debido a un error crítico.")
#             else:
#                 done = True
        
#         def session_stopped_cb(evt):
#             nonlocal done
#             # print("Session stopped event.")
#             done = True
        
#         # Conectar eventos
#         speech_recognizer.recognizing.connect(recognizing_cb)
#         speech_recognizer.recognized.connect(recognized_cb)
#         speech_recognizer.canceled.connect(canceled_cb)
#         speech_recognizer.session_stopped.connect(session_stopped_cb)
        
#         # Iniciar reconocimiento continuo
#         speech_recognizer.start_continuous_recognition()
        
#         # Esperar a que termine el reconocimiento
#         while not done:
#             import time
#             time.sleep(0.1)
        
#         # Detener reconocimiento
#         speech_recognizer.stop_continuous_recognition()
        
#         texto_final = texto_completo.strip()
#         if texto_final:
#             print(f"✅ Transcripción exitosa: {texto_final}")
#             return texto_final
#         else:
#             print("❌ No se pudo transcribir el audio")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al transcribir con Azure: {e}")
#         return None

import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
import time
import subprocess
import config
from datetime import datetime
 
# Configuración de Azure Speech-to-Text
AZURE_SPEECH_KEY = config.AZURE_SPEECH_KEY
AZURE_SPEECH_REGION = config.AZURE_SPEECH_REGION
 
if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise ValueError("Azure Speech Key or Region is not set. Verifica tu archivo config.py.")
 
# Configuración global de Azure Speech
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.speech_recognition_language = "es-ES"
 
 
def convertir_ogg_a_wav(input_file, output_file):
    """
    Convierte archivo OGG a WAV usando ffmpeg (equivalente al Node.js)
    Azure necesita WAV en 16 kHz, mono
    """
    try:
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
            print(f"✅ Conversión exitosa: {output_file}")
            return True
        else:
            print(f"❌ Error en conversión ffmpeg: {result.stderr}")
            return False
           
    except subprocess.TimeoutExpired:
        print("❌ Timeout en conversión ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error al convertir OGG a WAV: {e}")
        return False
 
 
def transcribir_audio_continuo(path):
    """
    Transcribe un archivo de audio WAV usando Azure Speech-to-Text con reconocimiento continuo
    Equivalente a transcribirAudioContinuo del Node.js
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"El archivo de audio no existe en la ruta: {path}")
       
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
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                print("NOMATCH: Speech could not be recognized.")
       
        def canceled_cb(evt):
            nonlocal done, error_occurred
            if evt.reason == speechsdk.CancellationReason.Error:
                error_occurred = True
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
            print(f"✅ Transcripción exitosa: {texto_final}")
            return texto_final
        else:
            print("❌ No se pudo transcribir el audio")
            return None
           
    except Exception as e:
        print(f"❌ Error al transcribir con Azure: {e}")
        return None
 
 
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
 
 
def procesar_audio_completo(audio_buffer, number):
    """
    Procesa un buffer de audio completo: guarda como OGG, convierte a WAV y transcribe
    Equivalente a handlerAI del Node.js
    """
    path_tmp_ogg = None
    path_tmp_wav = None
   
    try:
        # Crear directorio tmp si no existe
        tmp_folder = 'tmp'
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)
            print(f"📁 Directorio temporal creado: {tmp_folder}")
       
        # Generar nombres de archivos temporales
        timestamp = int(time.time() * 1000)  # Equivalente a Date.now()
        path_tmp_ogg = os.path.join(tmp_folder, f"voice-note-{timestamp}.ogg")
        path_tmp_wav = os.path.join(tmp_folder, f"voice-note-{timestamp}.wav")
       
        # Guardar archivo OGG
        with open(path_tmp_ogg, 'wb') as f:
            f.write(audio_buffer)
        print(f"✅ Archivo OGG guardado: {path_tmp_ogg}")
       
        # Convertir a WAV
        if not convertir_ogg_a_wav(path_tmp_ogg, path_tmp_wav):
            raise Exception("Error en conversión OGG a WAV")
       
        # Transcribir audio
        texto_transcrito = transcribir_audio_continuo(path_tmp_wav)
       
        return texto_transcrito
       
    except Exception as e:
        print(f"❌ Error al procesar audio completo: {e}")
        return None
       
    finally:
        # Eliminar archivos temporales
        try:
            if path_tmp_ogg and os.path.exists(path_tmp_ogg):
                os.remove(path_tmp_ogg)
                print(f"🗑️ Archivo OGG temporal eliminado: {path_tmp_ogg}")
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo OGG: {e}")
           
        try:
            if path_tmp_wav and os.path.exists(path_tmp_wav):
                os.remove(path_tmp_wav)
                print(f"🗑️ Archivo WAV temporal eliminado: {path_tmp_wav}")
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo WAV: {e}")
 
 
def procesar_audio_desde_url(media_url, number, whatsapp_token):
    """
    Descarga audio desde URL de WhatsApp y lo procesa
    """
    try:
        import requests
       
        print(f"📥 Descargando audio desde URL: {media_url}")
       
        # Descargar archivo con headers de autorización
        headers = {
            "Authorization": f"Bearer {whatsapp_token}"
        }
       
        response = requests.get(media_url, headers=headers, stream=True)
       
        if response.status_code == 200:
            # Obtener el buffer de audio
            audio_buffer = response.content
           
            # Procesar el audio completo
            texto_transcrito = procesar_audio_completo(audio_buffer, number)
           
            return texto_transcrito
        else:
            print(f"❌ Error al descargar audio: {response.status_code}")
            return None
           
    except Exception as e:
        print(f"❌ Error al procesar audio desde URL: {e}")
        return None
 
 
def convertir_audio_a_wav(audio_file_path):
    """
    Función de compatibilidad - convierte cualquier formato a WAV usando ffmpeg
    """
    try:
        print(f"🔄 Convirtiendo audio a WAV: {audio_file_path}")
       
        # Crear directorio audios_tmp si no existe
        audios_tmp_folder = 'audios_tmp'
        if not os.path.exists(audios_tmp_folder):
            os.makedirs(audios_tmp_folder)
            print(f"📁 Directorio temporal creado: {audios_tmp_folder}")
       
        # Crear archivo temporal para el WAV
        wav_filename = f"temp_{os.path.basename(audio_file_path).rsplit('.', 1)[0]}.wav"
        wav_file_path = os.path.join(audios_tmp_folder, wav_filename)
       
        # Usar ffmpeg para conversión
        if convertir_ogg_a_wav(audio_file_path, wav_file_path):
            return wav_file_path
        else:
            return None
           
    except Exception as e:
        print(f"❌ Error al convertir audio a WAV: {e}")
        return None
 
def transcribir_audio_con_azure(wav_file_path):
    """
    Función de compatibilidad - transcribe archivo WAV usando reconocimiento continuo
    """
    return transcribir_audio_continuo(wav_file_path)