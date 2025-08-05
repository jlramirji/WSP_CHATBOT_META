
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import asyncio
import config

# Configuración de Azure Speech-to-Text
AZURE_SPEECH_KEY = config.AZURE_SPEECH_KEY
AZURE_SPEECH_REGION = config.AZURE_SPEECH_REGION

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise ValueError("Azure Speech Key or Region is not set. Verifica tu archivo config.py.")

# Configuración global de Azure Speech
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.speech_recognition_language = "es-ES"


def convertir_audio_a_wav(audio_file_path):
    """
    Convierte un archivo de audio a formato WAV usando pydub
    Guarda el archivo WAV temporal en la carpeta audios_tmp
    """
    try:
        print(f"🔄 Convirtiendo audio a WAV: {audio_file_path}")
        
        # Cargar el archivo de audio
        audio = AudioSegment.from_file(audio_file_path)
        
        # Crear directorio audios_tmp si no existe
        audios_tmp_folder = 'audios_tmp'
        if not os.path.exists(audios_tmp_folder):
            os.makedirs(audios_tmp_folder)
            print(f"📁 Directorio temporal creado: {audios_tmp_folder}")
        
        # Crear archivo temporal para el WAV en la carpeta audios_tmp
        wav_filename = f"temp_{os.path.basename(audio_file_path).rsplit('.', 1)[0]}.wav"
        wav_file_path = os.path.join(audios_tmp_folder, wav_filename)
        
        # Exportar como WAV (16kHz, mono, 16-bit)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_file_path, format='wav')
        
        print(f"✅ Audio convertido a WAV temporal: {wav_file_path}")
        return wav_file_path
        
    except Exception as e:
        print(f"❌ Error al convertir audio a WAV: {e}")
        return None

def transcribir_audio_con_azure(wav_file_path):
    """
    Transcribe un archivo de audio WAV usando Azure Speech-to-Text con reconocimiento continuo
    """
    try:
        if not os.path.exists(wav_file_path):
            raise FileNotFoundError(f"El archivo de audio no existe en la ruta: {wav_file_path}")
        
        print(f"🎤 Transcribiendo audio con Azure (reconocimiento continuo): {wav_file_path}")
        
        # Configurar entrada de audio desde archivo
        audio_config = speechsdk.audio.AudioConfig(filename=wav_file_path)
        
        # Crear reconocedor de voz
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        # Variables para almacenar el resultado
        texto_completo = ""
        done = False
        
        def recognizing_cb(evt):
            # print(f"RECOGNIZING: Text={evt.result.text}")
            pass
        
        def recognized_cb(evt):
            nonlocal texto_completo
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # print(f"RECOGNIZED: Text={evt.result.text}")
                texto_completo += evt.result.text + " "
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                print("NOMATCH: Speech could not be recognized.")
        
        def canceled_cb(evt):
            nonlocal done
            # print(f"CANCELED: Reason={evt.reason}")
            if evt.reason == speechsdk.CancellationReason.Error:
                # print(f"CANCELED: ErrorCode={evt.error_code}")
                # print(f"CANCELED: ErrorDetails={evt.error_details}")
                raise Exception("La transcripción fue cancelada debido a un error crítico.")
            else:
                done = True
        
        def session_stopped_cb(evt):
            nonlocal done
            # print("Session stopped event.")
            done = True
        
        # Conectar eventos
        speech_recognizer.recognizing.connect(recognizing_cb)
        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.canceled.connect(canceled_cb)
        speech_recognizer.session_stopped.connect(session_stopped_cb)
        
        # Iniciar reconocimiento continuo
        speech_recognizer.start_continuous_recognition()
        
        # Esperar a que termine el reconocimiento
        while not done:
            import time
            time.sleep(0.1)
        
        # Detener reconocimiento
        speech_recognizer.stop_continuous_recognition()
        
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