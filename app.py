from flask import Flask, request, jsonify
import requests
from Funciones_bd.buscar_idnovedad import buscar_idnovedad
import util
import whatsappservice
import time
from Funciones_bd import buscar_usuario, insertar_bd_azure
from Funciones_py import leer_archivos,archivos_adjuntos,procesar_audio
from datetime import datetime, timedelta
import threading
import unicodedata
import json
import os
import mimetypes
from urllib.parse import urlparse
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import tempfile
import config

#from Funciones_bd.buscar_usuario import BuscarNombrexTelefono

# ==================== CONFIGURACIÓN DE ARCHIVOS ====================
# Directorio para almacenar archivos descargados
UPLOAD_FOLDER = config.UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Directorio para almacenar archivos adjuntos organizados
ADJUNTOS_FOLDER = config.ADJUNTOS_FOLDER
if not os.path.exists(ADJUNTOS_FOLDER):
    os.makedirs(ADJUNTOS_FOLDER)

# Configuración de WhatsApp API
WHATSAPP_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_API_URL = config.WHATSAPP_API_URL

# Configuración de Azure Speech-to-Text
AZURE_SPEECH_KEY = config.AZURE_SPEECH_KEY
AZURE_SPEECH_REGION = config.AZURE_SPEECH_REGION
 
user_sessions = {}
## Variables para almacenar fechas
fechahoy = datetime.now().date()
 
app = Flask(__name__)
@app.route('/welcome', methods  = ['GET'])
def index():
    return "Bienvenido al chatbot reporte novedades!"

@app.route('/admin/limpiar-sesiones', methods=['POST'])
def limpiar_sesiones_admin():
    """
    Endpoint de administración para limpiar todas las sesiones
    """
    try:
        # Limpiar TODAS las sesiones manualmente
        sesiones_eliminadas = limpiar_sesiones_por_comando()
        
        return {
            "status": "success",
            "message": f"Limpieza manual completada. Sesiones eliminadas: {sesiones_eliminadas}",
            "sesiones_eliminadas": sesiones_eliminadas
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al limpiar sesiones: {str(e)}"
        }, 500

@app.route('/admin/estado-sesiones', methods=['GET'])
def estado_sesiones():
    """
    Endpoint de administración para ver el estado de las sesiones
    """
    try:
        sesiones_info = {}
        ahora = time.time()
        
        for number, session in user_sessions.items():
            last_active = session.get('last_active', 0)
            tiempo_inactivo = int(ahora - last_active)
            
            sesiones_info[number] = {
                "ultima_actividad": tiempo_inactivo,
                "estado": session.get('esperando', 'activo'),
                "datos": {k: v for k, v in session.items() if k != 'last_active'}
            }
        
        return {
            "status": "success",
            "total_sesiones": len(user_sessions),
            "sesiones": sesiones_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener estado: {str(e)}"
        }, 500

@app.route('/admin/estado-webhook', methods=['GET'])
def estado_webhook():
    """
    Endpoint para verificar el estado del webhook y configuración
    """
    try:
        return {
            "status": "success",
            "webhook_activo": True,
            "configuracion": {
                "whatsapp_token": "Configurado" if WHATSAPP_TOKEN else "No configurado",
                "whatsapp_api_url": WHATSAPP_API_URL,
                "upload_folder": UPLOAD_FOLDER,
                "sesiones_activas": len(user_sessions)
            },
            "ultima_verificacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al verificar estado: {str(e)}"
        }, 500

@app.route('/admin/mensajes-procesados', methods=['GET'])
def mensajes_procesados():
    """
    Endpoint para verificar mensajes procesados y detectar duplicados
    """
    try:
        processed_messages = getattr(app, 'processed_messages', set())
        return {
            "status": "success",
            "total_mensajes_procesados": len(processed_messages),
            "mensajes_recientes": list(processed_messages)[-10:] if processed_messages else [],
            "ultima_verificacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener mensajes procesados: {str(e)}"
        }, 500

@app.route('/admin/limpiar-mensajes', methods=['POST'])
def limpiar_mensajes_procesados():
    """
    Endpoint para limpiar la lista de mensajes procesados
    """
    try:
        if hasattr(app, 'processed_messages'):
            total_eliminados = len(app.processed_messages)
            app.processed_messages.clear()
            return {
                "status": "success",
                "message": f"Lista de mensajes procesados limpiada. {total_eliminados} mensajes eliminados."
            }
        else:
            return {
                "status": "success",
                "message": "No hay mensajes procesados para limpiar."
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al limpiar mensajes: {str(e)}"
        }, 500

@app.route('/admin/archivos', methods=['GET'])
def listar_archivos():
    """
    Endpoint de administración para listar archivos descargados y organizados
    """
    try:
        archivos_temp = []
        archivos_organizados = []
        
        # Listar archivos temporales
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    info = archivos_adjuntos.obtener_info_archivo(filepath)
                    if info:
                        archivos_temp.append({
                            "nombre": filename,
                            "ruta": info['ruta'],
                            "tamaño_mb": info['tamaño_mb'],
                            "fecha_creacion": info['fecha_creacion'],
                            "extension": info['extension'],
                            "tipo": "temporal"
                        })
        
        # Listar archivos organizados por incidente
        if os.path.exists(ADJUNTOS_FOLDER):
            for incidente_id in os.listdir(ADJUNTOS_FOLDER):
                carpeta_incidente = os.path.join(ADJUNTOS_FOLDER, incidente_id)
                if os.path.isdir(carpeta_incidente):
                    incidente_archivos = []
                    for filename in os.listdir(carpeta_incidente):
                        filepath = os.path.join(carpeta_incidente, filename)
                        if os.path.isfile(filepath):
                            info = archivos_adjuntos.obtener_info_archivo(filepath)
                            if info:
                                incidente_archivos.append({
                                    "nombre": filename,
                                    "ruta": info['ruta'],
                                    "tamaño_mb": info['tamaño_mb'],
                                    "fecha_creacion": info['fecha_creacion'],
                                    "extension": info['extension'],
                                    "tipo": "organizado"
                                })
                    
                    if incidente_archivos:
                        # Ordenar archivos del incidente por fecha
                        incidente_archivos.sort(key=lambda x: x['fecha_creacion'], reverse=True)
                        archivos_organizados.append({
                            'incidente_id': incidente_id,
                            'total_archivos': len(incidente_archivos),
                            'archivos': incidente_archivos
                        })
        
        # Ordenar incidentes por ID (más recientes primero)
        archivos_organizados.sort(key=lambda x: int(x['incidente_id']), reverse=True)
        
        return {
            "status": "success",
            "archivos_temporales": {
                "total": len(archivos_temp),
                "directorio": UPLOAD_FOLDER,
                "archivos": archivos_temp
            },
            "archivos_organizados": {
                "total_incidentes": len(archivos_organizados),
                "directorio": ADJUNTOS_FOLDER,
                "incidentes": archivos_organizados
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al listar archivos: {str(e)}"
        }, 500

@app.route('/admin/archivos/<filename>', methods=['GET'])
def descargar_archivo_admin(filename):
    """
    Endpoint de administración para descargar un archivo específico
    """
    try:
        from flask import send_file
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": "Archivo no encontrado"
            }, 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al descargar archivo: {str(e)}"
        }, 500

@app.route('/admin/adjuntos/<incidente_id>/<filename>', methods=['GET'])
def descargar_adjunto_admin(incidente_id, filename):
    """
    Endpoint de administración para descargar un archivo adjunto organizado
    """
    try:
        from flask import send_file
        
        filepath = os.path.join(ADJUNTOS_FOLDER, incidente_id, filename)
        
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": "Archivo adjunto no encontrado"
            }, 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al descargar archivo adjunto: {str(e)}"
        }, 500
 
@app.route('/whatsapp', methods=['GET'])
def VerifyToken():

    try:
        accessToken = config.VERIFY_TOKEN
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token != None and challenge != None and token == accessToken:
            return challenge
        else:
            return "", 400

    except Exception as e:
        print(f"Error en verify_token: {e}")
        return "", 400

@app.route('/whatsapp', methods=['POST'])
def receive_message():
    try:
        body = request.get_json()
        
        # Verificar que el body no esté vacío
        if not body:
            print("⚠️ Webhook recibido con body vacío")
            return "EVENT_RECEIVED"
            
        #print("\n🔵 Webhook recibido:")
        #print(json.dumps(body, indent=2))  # Log completo del evento

        # Extraer datos principales del webhook
        entry = body.get("entry", [])
        if not entry:
            print("⚠️ No se encontró 'entry' en el webhook")
            return "EVENT_RECEIVED"
            
        changes = entry[0].get("changes", [])
        if not changes:
            print("⚠️ No se encontró 'changes' en el webhook")
            return "EVENT_RECEIVED"
            
        value = changes[0].get("value", {})
        if not value:
            print("⚠️ No se encontró 'value' en el webhook")
            return "EVENT_RECEIVED"

        # SOLO procesar si hay mensajes de usuario (no status updates, delivery receipts, etc.)
        if "messages" not in value or not value["messages"]:
            #print("🟡 Evento sin mensaje de usuario. Tipos de evento:", list(value.keys()))
            #print("🟡 Ignorando evento (status, delivery, etc.)")
            return "EVENT_RECEIVED"

        message = value["messages"][0]
        message_type = message.get("type", "")

        # Extraer número del usuario
        number = message["from"]
        
        # Validar timestamp del mensaje para evitar procesar mensajes antiguos
        message_timestamp = int(message.get("timestamp", 0))
        current_time = int(time.time())
        time_difference = current_time - message_timestamp
        
        #print(f"📅 Timestamp del mensaje: {message_timestamp}")
        #print(f"📅 Tiempo actual: {current_time}")
        #print(f"📅 Diferencia de tiempo: {time_difference} segundos")
        
        # Rechazar mensajes con más de 5 minutos de antigüedad
        # Para producción, cambiar a 120 segundos (2 minutos)
        if time_difference > 300:  # 5 minutos = 300 segundos
            print(f"⚠️ Mensaje rechazado por ser muy antiguo ({time_difference} segundos)")
            return "EVENT_RECEIVED"
        
        # Validar ID único del mensaje para evitar duplicados
        message_id = message.get("id", "")
        if not message_id:
            #print("⚠️ Mensaje rechazado: sin ID único")
            return "EVENT_RECEIVED"
        
        # Verificar si ya procesamos este mensaje
        if hasattr(app, 'processed_messages') and message_id in app.processed_messages:
            #print(f"⚠️ Mensaje duplicado detectado: {message_id}")
            return "EVENT_RECEIVED"
        
        # Agregar a la lista de mensajes procesados
        if not hasattr(app, 'processed_messages'):
            app.processed_messages = set()
        app.processed_messages.add(message_id)
        
        # Limpiar mensajes antiguos de la lista (mantener solo los últimos 1000)
        if len(app.processed_messages) > 1000:
            # Convertir a lista, tomar los últimos 1000 y volver a set
            app.processed_messages = set(list(app.processed_messages)[-1000:])
        
        #print(f"🟢 Mensaje válido recibido de: {number}")
        #print(f"📨 Tipo de mensaje: {message_type}")
        #print(f"🆔 ID del mensaje: {message_id}")
        #print(f"📅 Fecha del mensaje: {datetime.fromtimestamp(message_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        #print(f"📅 Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        #print(f"⏱️ Diferencia de tiempo: {time_difference} segundos")
        #print(f"📊 Total mensajes procesados: {len(getattr(app, 'processed_messages', set()))}")
        #print("-" * 50)

        # SOLO procesar tipos de mensaje específicos
        if message_type == "text":
            # Procesar mensaje de texto
            text = util.GetTextUser(message)
            print(f"📨 Texto del mensaje: {text}")
            # SOLO procesar si hay texto real
            if text and text.strip():
                ProcessMesages(text, number)
            else:
                print("⚠️ Mensaje de texto vacío, ignorando")
            
        elif message_type == "interactive":
            # Procesar mensaje interactivo (botones, listas)
            text = util.GetTextUser(message)
            print(f"📨 Texto del mensaje interactivo: {text}")
            if text and text.strip():
                ProcessMesages(text, number)
            else:
                print("⚠️ Mensaje interactivo sin texto, ignorando")
            
        elif message_type in ["audio", "image", "video", "document", "voice"]:
            # Procesar archivos si el usuario está en el estado correcto
            if number in user_sessions and user_sessions[number].get('esperando') in ['nota_de_voz', 'esperando_fotosvideos']:
        #        print(f"📎 Procesando archivo adjunto de tipo: {message_type}")
                filepath = archivos_adjuntos.procesar_archivo_adjunto(message, number, UPLOAD_FOLDER, user_sessions)
                
                if filepath:
                    if message_type == "audio":
                        mensaje_confirmacion = f"📎 Archivo {message_type} recibido y guardado."# Archivo: {os.path.basename(filepath)}"
                        #whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje_confirmacion, number))
                    else:
                        # Si estamos esperando fotos/videos, manejar múltiples archivos
                        if user_sessions[number].get('esperando') == 'esperando_fotosvideos':
                            # Inicializar contador de archivos si no existe
                            if 'archivos_procesados' not in user_sessions[number]:
                                user_sessions[number]['archivos_procesados'] = 0
                                user_sessions[number]['ultimo_archivo_time'] = time.time()
                                # Enviar mensaje inicial de procesamiento solo la primera vez
                                whatsappservice.SendMessageWhatsApp(util.TextMessage("🔄 Procesando archivos, espera un momento por favor...", number))
                            
                            # Cancelar timer anterior si existe
                            if 'timer_finalizacion' in user_sessions[number]:
                                try:
                                    user_sessions[number]['timer_finalizacion'].cancel()
                                except:
                                    pass
                            
                            # Incrementar contador
                            user_sessions[number]['archivos_procesados'] += 1
                            user_sessions[number]['ultimo_archivo_time'] = time.time()
                            
                            print(f"📎 Archivo {message_type} #{user_sessions[number]['archivos_procesados']} procesado correctamente")
                            
                            # Programar finalización después de 30 segundos de inactividad
                            timer = threading.Timer(30.0, lambda: finalizar_si_no_hay_mas_archivos(number))
                            user_sessions[number]['timer_finalizacion'] = timer
                            timer.start()
                        else:
                            # Para otros estados (nota_de_voz), comportamiento normal
                            mensaje_confirmacion = f"📎 Archivo {message_type} recibido y guardado."# Archivo: {os.path.basename(filepath)}"
                            whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje_confirmacion, number))
                else:
                    whatsappservice.SendMessageWhatsApp(util.TextMessage("❌ Error al procesar el archivo adjunto. Por favor, intenta nuevamente.", number))
            else:
                print(f"⚠️ Archivo {message_type} recibido pero usuario no está en estado correcto")
                whatsappservice.SendMessageWhatsApp(util.TextMessage("❌ Por favor, sigue el flujo de conversación. Escribe 'hola' para comenzar.", number))
            
        else:
            print(f"🟡 Mensaje de tipo '{message_type}' no soportado.")
            return "EVENT_RECEIVED"

        return "EVENT_RECEIVED"

    except Exception as e:
        print("🔴 Error al procesar el webhook:")
        print(e)
        return "EVENT_RECEIVED"


 
########################      FUNCIONES PRINCIPALES   ###################

def quitar_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

# ==================== GESTIÓN DE SESIONES ====================

def registrar_datos_en_bd(number):
    """
    Registra los datos de la sesión en la base de datos
    """
    try:
        if number not in user_sessions:
            print(f"❌ No se encontró sesión para {number}")
            return False
            
        datos = user_sessions[number]
        fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Crear descripción completa de archivos adjuntos
        descripcion_archivos = []
        
        # Procesar imágenes
        if 'imagenes_descargadas' in datos and datos['imagenes_descargadas']:
            for i, archivo in enumerate(datos['imagenes_descargadas'], 1):
                info_archivo = archivos_adjuntos.obtener_info_archivo(archivo)
                descripcion = f"{os.path.basename(archivo)}"
                if info_archivo:
                    descripcion += f" ({info_archivo['tamaño_mb']} MB)"
                descripcion_archivos.append(descripcion)
        
        # Procesar videos
        if 'videos_descargados' in datos and datos['videos_descargados']:
            for i, archivo in enumerate(datos['videos_descargados'], 1):
                info_archivo = archivos_adjuntos.obtener_info_archivo(archivo)
                descripcion = f"Video {i}: {os.path.basename(archivo)}"
                if info_archivo:
                    descripcion += f" ({info_archivo['tamaño_mb']} MB)"
                descripcion_archivos.append(descripcion)
        
        # Procesar documentos
        if 'documentos_descargados' in datos and datos['documentos_descargados']:
            for i, archivo in enumerate(datos['documentos_descargados'], 1):
                info_archivo = archivos_adjuntos.obtener_info_archivo(archivo)
                descripcion = f"Documento {i}: {os.path.basename(archivo)}"
                if info_archivo:
                    descripcion += f" ({info_archivo['tamaño_mb']} MB)"
                descripcion_archivos.append(descripcion)
        
        # Procesar audios/notas de voz
        if 'audio_descargado' in datos and datos['audio_descargado']:
            info_archivo = archivos_adjuntos.obtener_info_archivo(datos['audio_descargado'])
            descripcion = f"Audio: {os.path.basename(datos['audio_descargado'])}"
            if info_archivo:
                descripcion += f" ({info_archivo['tamaño_mb']} MB)"
            descripcion_archivos.append(descripcion)
        
        if 'nota_voz_descargada' in datos and datos['nota_voz_descargada']:
            info_archivo = archivos_adjuntos.obtener_info_archivo(datos['nota_voz_descargada'])
            descripcion = f"Nota de voz: {os.path.basename(datos['nota_voz_descargada'])}"
            if info_archivo:
                descripcion += f" ({info_archivo['tamaño_mb']} MB)"
            descripcion_archivos.append(descripcion)
        
        # Crear texto del reporte (solo la transcripción de audio)
        texto_reporte = datos.get('nota_de_voz', '')
        
        # Crear campo separado para adjuntos
        adjuntos = ""
        if descripcion_archivos:
            adjuntos = "\n".join([f"• {desc}" for desc in descripcion_archivos])

        Insertarincidente = {
            "nombrereportante": datos.get('nombrereportante', ''),
            "cedulareportante": datos.get('cedulareportante', ''),
            "codigoreportante": datos.get('usuarioreportante', ''),
            "telefonoreportante": number,
            "nombrereportado": datos.get('nombrereportado', '').upper(),
            "cedulareportado": datos.get('cedulareportado', ''),
            "codigoreportado": datos.get('usuarioreportado', '').upper(),
            "municipio": datos.get('municipio', '').upper(),
            "lugar": datos.get('lugar', ''),
            "fechaincidente": datos.get('fechanovedad', ''),
            "fechahorareportado": fecha_hora_actual,
            "textoreporte": texto_reporte,
            "adjuntos": adjuntos,
        }

        # Llama a la función para insertar el incidente en la base de datos
        incidente_id = insertar_bd_azure.insertar_incidente(Insertarincidente)
        innovedad = buscar_idnovedad()

        if innovedad and innovedad.get('idnovedad') is not None:
            print(f"✅ Datos registrados exitosamente en BD para {number} con ID: {incidente_id}")
            
            # Organizar archivos adjuntos en carpetas estructuradas
            if descripcion_archivos:
                if organizar_archivos_adjuntos(number, innovedad['idnovedad']):
                    print(f"📁 Archivos adjuntos organizados en carpeta {incidente_id}")
                else:
                    print(f"⚠️ No se pudieron organizar archivos adjuntos para incidente {incidente_id}")
            
            # Log de información registrada
            print(f"📝 Texto del reporte para {number}: {texto_reporte[:100]}{'...' if len(texto_reporte) > 100 else ''}")
            if adjuntos:
                print(f"📎 Archivos adjuntos registrados para {number}:")
                for desc in descripcion_archivos:
                    print(f"   - {desc}")
            else:
                print(f"📎 No hay archivos adjuntos para {number}")
            
            return True
        else:
            print(f"❌ Error al obtener ID del incidente para {number}")
            return False
        
    except Exception as e:
        print(f"❌ Error al registrar datos en BD para {number}: {e}")
        return False

def finalizar_sesion_exitosa(number, mensaje_final="✅ Gracias por tu reporte, te esperamos pronto!! 😊"):
    """
    Finaliza la sesión después de completar un reporte exitosamente
    """
    try:
        # Primero registrar los datos en la base de datos
        if registrar_datos_en_bd(number):
            # Enviar mensaje de confirmación
            whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje_final, number))
            
            # Limpiar datos de la sesión
            limpiar_datos_sesion(number)
            
            print(f"✅ Sesión finalizada exitosamente para {number}")
        else:
            # Si falla el registro en BD, enviar mensaje de error
            mensaje_error = "❌ Lo sentimos, hubo un error al registrar tu reporte. intentaremos registrarlo nuevamente.\n\n Espera un momento por favor..."
            whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje_error, number))
            print(f"❌ No se pudo finalizar sesión para {number} - Error en registro BD")
        
    except Exception as e:
        print(f"❌ Error al finalizar sesión exitosa para {number}: {e}")

def finalizar_sesion_usuario(number, mensaje_despedida="¡Gracias por contactarnos! Si necesitas más ayuda, no dudes en escribirnos de nuevo. 😊"):
    """
    Finaliza la sesión cuando el usuario solicita salir
    """
    try:
        # Enviar mensaje de despedida
        whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje_despedida, number))
        
        # Limpiar datos de la sesión
        limpiar_datos_sesion(number)
        
        print(f"👋 Sesión finalizada por solicitud del usuario {number}")
        
    except Exception as e:
        print(f"❌ Error al finalizar sesión por usuario para {number}: {e}")

def finalizar_sesion_timeout(number, mensaje_timeout="⏰ Tu sesión ha sido cerrada automáticamente por inactividad. Si deseas continuar, escribe *Hola* para iniciar una nueva sesión."):
    """
    Finaliza la sesión por inactividad (timeout)
    """
    try:
        # Enviar mensaje de timeout
        whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje_timeout, number))
        
        # Limpiar datos de la sesión
        limpiar_datos_sesion(number)
        
        print(f"⏰ Sesión finalizada por timeout para {number}")
        
    except Exception as e:
        print(f"❌ Error al finalizar sesión por timeout para {number}: {e}")

def limpiar_datos_sesion(number):
    """
    Limpia completamente los datos de la sesión del usuario (archivos ya organizados)
    """
    try:
        if number in user_sessions:
            # Cancelar timer de finalización si existe
            if 'timer_finalizacion' in user_sessions[number]:
                try:
                    user_sessions[number]['timer_finalizacion'].cancel()
                except:
                    pass
            
            # Obtener datos antes de eliminar (para logging)
            datos_eliminados = user_sessions[number].copy()
            
            # NOTA: Los archivos ya fueron organizados en carpetas, no se eliminan
            print(f"📁 Archivos ya organizados en carpetas para {number}")
            
            # Eliminar la sesión
            del user_sessions[number]
            
            # Log de limpieza
            #print(f"🗑️ Datos eliminados para {number}:")
            for key, value in datos_eliminados.items():
                if key != 'last_active':  # No mostrar timestamp
                    print(f"   - {key}: {value}")
                    
    except Exception as e:
        print(f"❌ Error al limpiar datos de sesión para {number}: {e}")

def organizar_archivos_adjuntos(number, incidente_id):
    """
    Organiza los archivos adjuntos en carpetas estructuradas por ID de incidente
    """
    try:
        if number not in user_sessions:
            return False
            
        datos = user_sessions[number]
        archivos_organizados = []
        
        # Crear carpeta para el incidente
        carpeta_incidente = os.path.join(ADJUNTOS_FOLDER, str(incidente_id))
        if not os.path.exists(carpeta_incidente):
            os.makedirs(carpeta_incidente)
            print(f"📁 Carpeta creada: {carpeta_incidente}")
        
        # Mover imágenes
        if 'imagenes_descargadas' in datos and datos['imagenes_descargadas']:
            for i, archivo_original in enumerate(datos['imagenes_descargadas'], 1):
                if os.path.exists(archivo_original):
                    nombre_archivo = os.path.basename(archivo_original)
                    archivo_destino = os.path.join(carpeta_incidente, f"imagen_{i}_{nombre_archivo}")
                    os.rename(archivo_original, archivo_destino)
                    archivos_organizados.append(archivo_destino)
                    print(f"📸 Imagen organizada: {archivo_destino}")
        
        # Mover videos
        if 'videos_descargados' in datos and datos['videos_descargados']:
            for i, archivo_original in enumerate(datos['videos_descargados'], 1):
                if os.path.exists(archivo_original):
                    nombre_archivo = os.path.basename(archivo_original)
                    archivo_destino = os.path.join(carpeta_incidente, f"video_{i}_{nombre_archivo}")
                    os.rename(archivo_original, archivo_destino)
                    archivos_organizados.append(archivo_destino)
                    print(f"🎥 Video organizado: {archivo_destino}")
        
        # Mover documentos
        if 'documentos_descargados' in datos and datos['documentos_descargados']:
            for i, archivo_original in enumerate(datos['documentos_descargados'], 1):
                if os.path.exists(archivo_original):
                    nombre_archivo = os.path.basename(archivo_original)
                    archivo_destino = os.path.join(carpeta_incidente, f"documento_{i}_{nombre_archivo}")
                    os.rename(archivo_original, archivo_destino)
                    archivos_organizados.append(archivo_destino)
                    print(f"📄 Documento organizado: {archivo_destino}")
        
        # Mover archivos individuales (compatibilidad)
        archivos_individuales = [
            ('imagen_descargada', 'imagen_1'),
            ('video_descargado', 'video_1'),
            ('documento_descargado', 'documento_1'),
            ('audio_descargado', 'audio_1'),
            ('nota_voz_descargada', 'nota_voz_1')
        ]
        
        for clave, prefijo in archivos_individuales:
            if clave in datos and datos[clave]:
                archivo_original = datos[clave]
                if os.path.exists(archivo_original):
                    nombre_archivo = os.path.basename(archivo_original)
                    archivo_destino = os.path.join(carpeta_incidente, f"{prefijo}_{nombre_archivo}")
                    os.rename(archivo_original, archivo_destino)
                    archivos_organizados.append(archivo_destino)
                    print(f"📎 Archivo organizado: {archivo_destino}")
        
        if archivos_organizados:
            print(f"✅ {len(archivos_organizados)} archivos organizados en carpeta {incidente_id}")
            return True
        else:
            print(f"⚠️ No se encontraron archivos para organizar en incidente {incidente_id}")
            return False
        
    except Exception as e:
        print(f"❌ Error al organizar archivos adjuntos para {number}: {e}")
        return False

def limpiar_archivos_sesion(number):
    """
    Elimina todos los archivos físicos asociados a una sesión
    """
    try:
        if number not in user_sessions:
            return
            
        datos = user_sessions[number]
        archivos_eliminados = []
        
        # Eliminar imágenes
        if 'imagenes_descargadas' in datos:
            for archivo in datos['imagenes_descargadas']:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    archivos_eliminados.append(archivo)
                    print(f"🗑️ Imagen eliminada: {archivo}")
        
        # Eliminar videos
        if 'videos_descargados' in datos:
            for archivo in datos['videos_descargados']:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    archivos_eliminados.append(archivo)
                    print(f"🗑️ Video eliminado: {archivo}")
        
        # Eliminar documentos
        if 'documentos_descargados' in datos:
            for archivo in datos['documentos_descargados']:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    archivos_eliminados.append(archivo)
                    print(f"🗑️ Documento eliminado: {archivo}")
        
        # Eliminar archivos individuales (compatibilidad)
        archivos_individuales = [
            'imagen_descargada', 'video_descargado', 'documento_descargado',
            'audio_descargado', 'nota_voz_descargada'
        ]
        
        for clave in archivos_individuales:
            if clave in datos and datos[clave]:
                archivo = datos[clave]
                if os.path.exists(archivo):
                    os.remove(archivo)
                    archivos_eliminados.append(archivo)
                    print(f"🗑️ Archivo eliminado: {archivo}")
        
        if archivos_eliminados:
            print(f"🗑️ {len(archivos_eliminados)} archivos eliminados para {number}")
        
    except Exception as e:
        print(f"❌ Error al limpiar archivos de sesión para {number}: {e}")

def verificar_timeout_sesiones():
    """
    Verifica y limpia sesiones inactivas
    """
    try:
        ahora = time.time()
        timeout_segundos = 300  # 5 minutos
        sesiones_a_limpiar = []
        
        for number, session in user_sessions.items():
            last_active = session.get('last_active', 0)
            if ahora - last_active > timeout_segundos:
                sesiones_a_limpiar.append(number)
        
        # Limpiar sesiones inactivas
        for number in sesiones_a_limpiar:
            finalizar_sesion_timeout(number)
            
        if sesiones_a_limpiar:
            print(f"🧹 Limpiadas {len(sesiones_a_limpiar)} sesiones inactivas")
            
    except Exception as e:
        print(f"❌ Error al verificar timeout de sesiones: {e}")

def limpiar_sesiones_por_comando():
    """
    Función para limpiar todas las sesiones manualmente
    """
    try:
        total_sesiones = len(user_sessions)
        user_sessions.clear()
        print(f"🧹 Limpieza manual: {total_sesiones} sesiones eliminadas")
        return total_sesiones
    except Exception as e:
        print(f"❌ Error en limpieza manual: {e}")
        return 0

def reiniciar_sesion(number):
    """
    Reinicia la sesión del usuario (limpia datos pero mantiene el número)
    """
    try:
        if number in user_sessions:
            print(f"🔄 Reiniciando sesión para {number}")
            limpiar_datos_sesion(number)
        
        # Crear nueva sesión limpia
        user_sessions[number] = {
            'last_active': time.time(),
            'estado': 'nueva_sesion'
        }
        
        print(f"✅ Sesión reiniciada para {number}")
        
    except Exception as e:
        print(f"❌ Error al reiniciar sesión para {number}: {e}")

# ==================== GESTIÓN DE ARCHIVOS ADJUNTOS ====================

# def obtener_media_url(media_id):
#     """
#     Obtiene la URL de descarga de un archivo de WhatsApp usando su media_id
#     """
#     try:
#         url = f"{WHATSAPP_API_URL}/{media_id}"
#         headers = {
#             "Authorization": f"Bearer {WHATSAPP_TOKEN}"
#         }
        
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             data = response.json()
#             return data.get('url')
#         else:
#             print(f"❌ Error al obtener URL de media: {response.status_code}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al obtener media URL: {e}")
#         return None

# def descargar_archivo(media_url, filename):
#     """
#     Descarga un archivo desde una URL y lo guarda localmente
#     """
#     try:
#         headers = {
#             "Authorization": f"Bearer {WHATSAPP_TOKEN}"
#         }
        
#         response = requests.get(media_url, headers=headers, stream=True)
        
#         if response.status_code == 200:
#             filepath = os.path.join(UPLOAD_FOLDER, filename)
            
#             with open(filepath, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)
            
#             print(f"✅ Archivo descargado: {filepath}")
#             return filepath
#         else:
#             print(f"❌ Error al descargar archivo: {response.status_code}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al descargar archivo: {e}")
#         return None

# def descargar_archivo_temporal(media_url, filename):
#     """
#     Descarga un archivo desde una URL y lo guarda temporalmente en la carpeta audios_tmp
#     """
#     try:
#         headers = {
#             "Authorization": f"Bearer {WHATSAPP_TOKEN}"
#         }
        
#         response = requests.get(media_url, headers=headers, stream=True)
        
#         if response.status_code == 200:
#             # Crear directorio audios_tmp si no existe
#             audios_tmp_folder = 'audios_tmp'
#             if not os.path.exists(audios_tmp_folder):
#                 os.makedirs(audios_tmp_folder)
#                 print(f"📁 Directorio temporal creado: {audios_tmp_folder}")
            
#             # Crear archivo temporal en la carpeta audios_tmp
#             temp_filepath = os.path.join(audios_tmp_folder, filename)
            
#             with open(temp_filepath, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)
            
#             print(f"✅ Archivo temporal descargado: {temp_filepath}")
#             return temp_filepath
#         else:
#             print(f"❌ Error al descargar archivo: {response.status_code}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al descargar archivo temporal: {e}")
#         return None

# def procesar_archivo_adjunto(message, number):
#     """
#     Procesa y descarga archivos adjuntos (audio, imagen, video, documento)
#     """
#     try:
#         message_type = message.get('type', '')
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
#         # Enviar mensaje de procesamiento para archivos de audio
#         if message_type in ['audio', 'voice']:
#             whatsappservice.SendMessageWhatsApp(
#                 util.TextMessage("🔄 Procesando nota de voz...", number)
#             )
        
#         if message_type == 'audio':
#             return procesar_audio(message, number, timestamp)
#         elif message_type == 'image':
#             return procesar_imagen(message, number, timestamp)
#         elif message_type == 'video':
#             return procesar_video(message, number, timestamp)
#         elif message_type == 'document':
#             return procesar_documento(message, number, timestamp)
#         elif message_type == 'voice':
#             return procesar_nota_voz(message, number, timestamp)
#         else:
#             print(f"⚠️ Tipo de archivo no soportado: {message_type}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al procesar archivo adjunto: {e}")
#         return None

# def procesar_audio(message, number, timestamp):
#     """
#     Procesa archivos de audio y los transcribe con Azure usando archivos temporales
#     """
#     try:
#         audio_data = message.get('audio', {})
#         media_id = audio_data.get('id')
        
#         if not media_id:
#             print("❌ No se encontró media_id en el audio")
#             return None
        
#         # Obtener URL de descarga
#         media_url = obtener_media_url(media_id)
#         if not media_url:
#             return None
        
#         # Generar nombre de archivo
#         filename = f"audio_{number}_{timestamp}.mp3"
        
#         # Descargar archivo temporalmente
#         temp_filepath = descargar_archivo_temporal(media_url, filename)
        
#         if temp_filepath:
#             print(f"🎵 Audio temporal descargado para {number}: {temp_filepath}")
            
#             # Procesar audio completo (convertir a WAV y transcribir)
#             texto_transcrito = procesar_audio_completo(temp_filepath, number)
            
#             if texto_transcrito:
#                 # Mostrar transcripción al usuario para validación
#                 mostrar_transcripcion_y_validar(number, texto_transcrito)
#             else:
#                 # Si falla la transcripción, enviar mensaje de error
#                 whatsappservice.SendMessageWhatsApp(
#                     util.TextMessage("❌ No se pudo transcribir el audio. Por favor, intenta enviar una nota de voz más clara o escribe tu mensaje.", number)
#                 )
            
#             return temp_filepath
        
#         return None
        
#     except Exception as e:
#         print(f"❌ Error al procesar audio: {e}")
#         return None

# def procesar_imagen(message, number, timestamp):
#     """
#     Procesa archivos de imagen
#     """
#     try:
#         image_data = message.get('image', {})
#         media_id = image_data.get('id')
        
#         if not media_id:
#             print("❌ No se encontró media_id en la imagen")
#             return None
        
#         # Obtener URL de descarga
#         media_url = obtener_media_url(media_id)
#         if not media_url:
#             return None
        
#         # Determinar extensión basada en mimetype
#         mimetype = image_data.get('mime_type', 'image/jpeg')
#         extension = mimetypes.guess_extension(mimetype) or '.jpg'
        
#         # Generar nombre de archivo
#         filename = f"imagen_{number}_{timestamp}{extension}"
        
#         # Descargar archivo
#         filepath = descargar_archivo(media_url, filename)
        
#         if filepath:
#             # Guardar información en la sesión del usuario
#             if number in user_sessions:
#                 # Inicializar lista si no existe
#                 if 'imagenes_descargadas' not in user_sessions[number]:
#                     user_sessions[number]['imagenes_descargadas'] = []
                
#                 # Agregar archivo a la lista
#                 user_sessions[number]['imagenes_descargadas'].append(filepath)
#                 user_sessions[number]['tipo_archivo'] = 'imagen'
                
#                 # Mantener compatibilidad con el código existente (último archivo)
#                 user_sessions[number]['imagen_descargada'] = filepath
            
#             print(f"🖼️ Imagen procesada para {number}: {filepath}")
#             return filepath
        
#         return None
        
#     except Exception as e:
#         print(f"❌ Error al procesar imagen: {e}")
#         return None

# def procesar_video(message, number, timestamp):
#     """
#     Procesa archivos de video
#     """
#     try:
#         video_data = message.get('video', {})
#         media_id = video_data.get('id')
        
#         if not media_id:
#             print("❌ No se encontró media_id en el video")
#             return None
        
#         # Obtener URL de descarga
#         media_url = obtener_media_url(media_id)
#         if not media_url:
#             return None
        
#         # Determinar extensión basada en mimetype
#         mimetype = video_data.get('mime_type', 'video/mp4')
#         extension = mimetypes.guess_extension(mimetype) or '.mp4'
        
#         # Generar nombre de archivo
#         filename = f"video_{number}_{timestamp}{extension}"
        
#         # Descargar archivo
#         filepath = descargar_archivo(media_url, filename)
        
#         if filepath:
#             # Guardar información en la sesión del usuario
#             if number in user_sessions:
#                 # Inicializar lista si no existe
#                 if 'videos_descargados' not in user_sessions[number]:
#                     user_sessions[number]['videos_descargados'] = []
                
#                 # Agregar archivo a la lista
#                 user_sessions[number]['videos_descargados'].append(filepath)
#                 user_sessions[number]['tipo_archivo'] = 'video'
                
#                 # Mantener compatibilidad con el código existente (último archivo)
#                 user_sessions[number]['video_descargado'] = filepath
            
#             print(f"🎥 Video procesado para {number}: {filepath}")
#             return filepath
        
#         return None
        
#     except Exception as e:
#         print(f"❌ Error al procesar video: {e}")
#         return None

# def procesar_documento(message, number, timestamp):
#     """
#     Procesa archivos de documento
#     """
#     try:
#         document_data = message.get('document', {})
#         media_id = document_data.get('id')
        
#         if not media_id:
#             print("❌ No se encontró media_id en el documento")
#             return None
        
#         # Obtener URL de descarga
#         media_url = obtener_media_url(media_id)
#         if not media_url:
#             return None
        
#         # Obtener nombre original del archivo
#         original_filename = document_data.get('filename', 'documento')
        
#         # Determinar extensión
#         mimetype = document_data.get('mime_type', 'application/octet-stream')
#         extension = mimetypes.guess_extension(mimetype) or '.bin'
        
#         # Generar nombre de archivo
#         filename = f"doc_{number}_{timestamp}_{original_filename}{extension}"
        
#         # Descargar archivo
#         filepath = descargar_archivo(media_url, filename)
        
#         if filepath:
#             # Guardar información en la sesión del usuario
#             if number in user_sessions:
#                 # Inicializar lista si no existe
#                 if 'documentos_descargados' not in user_sessions[number]:
#                     user_sessions[number]['documentos_descargados'] = []
                
#                 # Agregar archivo a la lista
#                 user_sessions[number]['documentos_descargados'].append(filepath)
#                 user_sessions[number]['tipo_archivo'] = 'documento'
                
#                 # Mantener compatibilidad con el código existente (último archivo)
#                 user_sessions[number]['documento_descargado'] = filepath
            
#             print(f"📄 Documento procesado para {number}: {filepath}")
#             return filepath
        
#         return None
        
#     except Exception as e:
#         print(f"❌ Error al procesar documento: {e}")
#         return None

# def procesar_nota_voz(message, number, timestamp):
#     """
#     Procesa notas de voz (voice messages) y las transcribe con Azure usando archivos temporales
#     """
#     try:
#         voice_data = message.get('voice', {})
#         media_id = voice_data.get('id')
        
#         if not media_id:
#             print("❌ No se encontró media_id en la nota de voz")
#             return None
        
#         # Obtener URL de descarga
#         media_url = obtener_media_url(media_id)
#         if not media_url:
#             return None
        
#         # Generar nombre de archivo
#         filename = f"nota_voz_{number}_{timestamp}.ogg"
        
#         # Descargar archivo temporalmente
#         temp_filepath = descargar_archivo_temporal(media_url, filename)
        
#         if temp_filepath:
#             print(f"🎤 Nota de voz temporal descargada para {number}: {temp_filepath}")
            
#             # Procesar audio completo (convertir a WAV y transcribir)
#             texto_transcrito = procesar_audio_completo(temp_filepath, number)
            
#             if texto_transcrito:
#                 # Mostrar transcripción al usuario para validación
#                 mostrar_transcripcion_y_validar(number, texto_transcrito)
#             else:
#                 # Si falla la transcripción, enviar mensaje de error
#                 whatsappservice.SendMessageWhatsApp(
#                     util.TextMessage("❌ No se pudo transcribir la nota de voz. Por favor, intenta enviar una nota más clara o escribe tu mensaje.", number)
#                 )
            
#             return temp_filepath
        
#         return None
        
#     except Exception as e:
#         print(f"❌ Error al procesar nota de voz: {e}")
#         return None

# def obtener_info_archivo(filepath):
#     """
#     Obtiene información del archivo descargado
#     """
#     try:
#         if not filepath or not os.path.exists(filepath):
#             return None
        
#         stat = os.stat(filepath)
#         return {
#             'ruta': filepath,
#             'tamaño_bytes': stat.st_size,
#             'tamaño_mb': round(stat.st_size / (1024 * 1024), 2),
#             'fecha_creacion': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
#             'extension': os.path.splitext(filepath)[1]
#         }
        
#     except Exception as e:
#         print(f"❌ Error al obtener info del archivo: {e}")
#         return None

# Función original comentada para referencia
# def limpiar_sesiones_inactivas():
#     while True:
#         ahora = time.time()
#         inactivos = []
#         for number, session in list(user_sessions.items()):
#             if 'last_active' in session and ahora - session['last_active'] > 300:  # 300 segundos = 5 minutos
#                 whatsappservice.SendMessageWhatsApp(
#                     util.TextMessage(
#                         "⏰ Tu sesión ha sido cerrada automáticamente por inactividad. Si deseas continuar, escribe *Hola* para iniciar una nueva sesión.",
#                         number
#                     )
#                 )
#                 inactivos.append(number)
#         for number in inactivos:
#             del user_sessions[number]
#         time.sleep(300)  # Revisa cada minuto

# # Inicia el hilo al arrancar la app
# threading.Thread(target=limpiar_sesiones_inactivas, daemon=True).start()

def enviar_mensajes_con_espera(mensajes, number, espera=3):
    ###Envía una lista de mensajes por WhatsApp con un tiempo de espera entre cada uno.
    for mensaje in mensajes:
        whatsappservice.SendMessageWhatsApp(
            util.TextMessage(mensaje, number)
        )
        time.sleep(espera)

def preguntar_municipio(number):
    whatsappservice.SendMessageWhatsApp(
        util.TextMessage("Por favor, escribe el *Nombre del Municipio* donde ocurrió la novedad.", number)
    )
    user_sessions[number]['esperando'] = 'municipio'
 
def preguntar_lugar(number):
    whatsappservice.SendMessageWhatsApp(
        util.TextMessage("Ahora, describe el *lugar exacto* donde ocurrió la novedad, puede ser una dirección o descripción del lugar.", number)
    )
    user_sessions[number]['esperando'] = 'lugar'
 
def preguntar_nota_de_voz(number):
    # Verificar si ya hay una transcripción válida
    if number in user_sessions and user_sessions[number].get('texto_transcrito'):
        # Ya hay una transcripción, preguntar si quiere usarla o enviar una nueva
        mensaje = [
            "🎤 Ya tienes una transcripción pendiente de validación.",
            "¿Deseas continuar con esa transcripción o enviar una nueva nota de voz?"
        ]
        enviar_mensajes_con_espera(mensaje, number, espera=2)
        
        # Enviar opciones
        whatsappservice.SendMessageWhatsApp(
            util.ListValidacionTranscripcion(number)
        )
        user_sessions[number]['esperando'] = 'validar_transcripcion'
    else:
        # No hay transcripción previa, pedir nueva nota de voz
        whatsappservice.SendMessageWhatsApp(
            util.TextMessage("Por favor, envía una *nota de voz*, 🗣 que sea clara y pausada describiendo de manera detallada lo sucedido.", number)
        )
        user_sessions[number]['esperando'] = 'nota_de_voz'

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
#     Transcribe un archivo de audio WAV usando Azure Speech-to-Text
#     """
#     try:
#         if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
#             print("❌ Variables de entorno AZURE_SPEECH_KEY o AZURE_SPEECH_REGION no configuradas")
#             return None
        
#         print(f"🎤 Transcribiendo audio con Azure: {wav_file_path}")
        
#         # Configurar Azure Speech SDK
#         speech_config = speechsdk.SpeechConfig(
#             subscription=AZURE_SPEECH_KEY, 
#             region=AZURE_SPEECH_REGION
#         )
        
#         # Configurar para español
#         speech_config.speech_recognition_language = "es-ES"
        
#         # Configurar entrada de audio desde archivo
#         audio_config = speechsdk.audio.AudioConfig(filename=wav_file_path)
        
#         # Crear reconocedor de voz
#         speech_recognizer = speechsdk.SpeechRecognizer(
#             speech_config=speech_config, 
#             audio_config=audio_config
#         )
        
#         # Realizar reconocimiento
#         result = speech_recognizer.recognize_once_async().get()
        
#         if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             texto_transcrito = result.text
#             print(f"✅ Transcripción exitosa: {texto_transcrito}")
#             return texto_transcrito
#         elif result.reason == speechsdk.ResultReason.NoMatch:
#             print(f"❌ No se pudo reconocer el audio: {result.no_match_details}")
#             return None
#         elif result.reason == speechsdk.ResultReason.Canceled:
#             print(f"❌ Reconocimiento cancelado: {result.cancellation_details}")
#             return None
#         else:
#             print(f"❌ Error en reconocimiento: {result.reason}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error al transcribir con Azure: {e}")
#         return None

# def procesar_audio_completo(audio_file_path, number):
#     """
#     Procesa un archivo de audio completo: convierte a WAV y transcribe con Azure
#     Limpia automáticamente los archivos temporales después del procesamiento
#     """
#     wav_file_path = None
#     try:
#         # Convertir a WAV
#         wav_file_path = convertir_audio_a_wav(audio_file_path)
#         if not wav_file_path:
#             return None
        
#         # Transcribir con Azure
#         texto_transcrito = transcribir_audio_con_azure(wav_file_path)
#         if not texto_transcrito:
#             return None
        
#         # Guardar información en la sesión del usuario
#         if number in user_sessions:
#             user_sessions[number]['texto_transcrito'] = texto_transcrito
#             user_sessions[number]['esperando'] = 'validar_transcripcion'
        
#         return texto_transcrito
        
#     except Exception as e:
#         print(f"❌ Error en procesamiento completo de audio: {e}")
#         return None
#     finally:
#         # Limpiar archivos temporales automáticamente
#         limpiar_archivos_audio_temporales(audio_file_path, wav_file_path)

# def mostrar_transcripcion_y_validar(number, texto_transcrito):
#     """
#     Muestra la transcripción al usuario y solicita validación
#     """
    
#     try:
#         # PRIMERO: Mostrar la transcripción
#         mensaje = [
#             f"🎤 *Transcripción del audio:*\n\n{texto_transcrito}"
#         ]
#         enviar_mensajes_con_espera(mensaje, number, espera=2)
       
#         # # Enviar opciones de validación
#         # whatsappservice.SendMessageWhatsApp(
#         #     util.ListValTranscr(number)
#         # )   
#         whatsappservice.SendMessageWhatsApp(
#             util.ButtonsValTranscr(number)
#         )        
        
#         print(f"✅ Transcripción enviada para validación a {number}")
        
#     except Exception as e:
#         print(f"❌ Error al mostrar transcripción: {e}")

def finalizar_si_no_hay_mas_archivos(number):
    """
    Finaliza la sesión si han pasado 30 segundos sin recibir nuevos archivos
    """
    try:
        if number not in user_sessions:
            return
            
        if user_sessions[number].get('esperando') != 'esperando_fotosvideos':
            return
            
        tiempo_actual = time.time()
        ultimo_archivo_time = user_sessions[number].get('ultimo_archivo_time', 0)
        tiempo_transcurrido = tiempo_actual - ultimo_archivo_time
        
        # Si han pasado más de 30 segundos desde el último archivo
        if tiempo_transcurrido >= 30.0:
            # Generar resumen de archivos adjuntos
            resumen_archivos = generar_resumen_archivos(number)
            
            if "No hay archivos adjuntos" in resumen_archivos:
                mensaje = ["✅ Gracias por tu reporte, te esperamos pronto!! 😊"]
            else:
                archivos_procesados = user_sessions[number].get('archivos_procesados', 0)
            mensaje = [f"✅ Procesamiento completado!\n\n{resumen_archivos}\n"]
            
            enviar_mensajes_con_espera(mensaje, number, espera=2)
            finalizar_sesion_exitosa(number)
            
    except Exception as e:
        print(f"❌ Error al finalizar sesión por timeout de archivos: {e}")

# def limpiar_archivos_audio_temporales(audio_file_path, wav_file_path=None):
#     """
#     Limpia archivos de audio temporales después del procesamiento
#     """
#     try:
#         # Eliminar archivo WAV temporal si existe
#         if wav_file_path and os.path.exists(wav_file_path):
#             os.remove(wav_file_path)
#             print(f"🗑️ Archivo WAV temporal eliminado: {wav_file_path}")
        
#         # Eliminar archivo de audio temporal original
#         if audio_file_path and os.path.exists(audio_file_path):
#             os.remove(audio_file_path)
#             print(f"🗑️ Archivo de audio temporal eliminado: {audio_file_path}")
        
#     except Exception as e:
#         print(f"❌ Error al limpiar archivos temporales: {e}")

def generar_resumen_archivos(number):
    """
    Genera un resumen de todos los archivos adjuntos para mostrar al usuario
    """
    try:
        if number not in user_sessions:
            return "No hay archivos adjuntos"
            
        datos = user_sessions[number]
        resumen = []
        total_archivos = 0
        
        # Contar imágenes
        if 'imagenes_descargadas' in datos and datos['imagenes_descargadas']:
            cantidad = len(datos['imagenes_descargadas'])
            total_archivos += cantidad
            resumen.append(f"\n📸 {cantidad} imagen{'es' if cantidad > 1 else ''}")
        
        # Contar videos
        if 'videos_descargados' in datos and datos['videos_descargados']:
            cantidad = len(datos['videos_descargados'])
            total_archivos += cantidad
            resumen.append(f"\n🎥 {cantidad} video{'s' if cantidad > 1 else ''}")
        
        # Contar documentos
        if 'documentos_descargados' in datos and datos['documentos_descargados']:
            cantidad = len(datos['documentos_descargados'])
            total_archivos += cantidad
            resumen.append(f"📄 {cantidad} documento{'s' if cantidad > 1 else ''}")
        
        # Contar audios
        if ('audio_descargado' in datos and datos['audio_descargado']) or ('nota_voz_descargada' in datos and datos['nota_voz_descargada']):
            total_archivos += 1
            resumen.append("🎵 1 audio")
        
        # Mostrar información adicional sobre archivos procesados
        archivos_procesados = datos.get('archivos_procesados', 0)
        if archivos_procesados > 0:
            resumen.append(f"\n✅ {archivos_procesados} archivo{'s' if archivos_procesados > 1 else ''} procesado{'s' if archivos_procesados > 1 else ''} correctamente")
        
        if total_archivos == 0:
            return "No hay archivos adjuntos"
        elif total_archivos == 1:
            return f"📎 1 archivo adjunto: {resumen[0]}"
        else:
            return f"📎 Archivos adjuntos: {', '.join(resumen)}"
            
    except Exception as e:
        print(f"❌ Error al generar resumen de archivos para {number}: {e}")
        return "Error al contar archivos"
 
 
############################################  Funcion principal para enviar datos  #######################

def ProcessMesages(text,number):
    # Solo procesa si hay texto real
    if not text or text.strip() == "":
        return  # No hacer nada si el mensaje está vacío
    
    #print("El texto recibido es: ", text)
    text = quitar_acentos(text.lower())
    #print("El texto en minusculas es: ", text)
    #listData=[]
 
    # Verificar timeout de sesiones antes de procesar
    verificar_timeout_sesiones()
    
    # SOLO inicializar sesión si el usuario envía un mensaje válido de inicio
    if number not in user_sessions:
        # NO crear sesión automáticamente, solo si es un mensaje de inicio válido
        if not ("hola" in text or "hello" in text or "hi" in text or "buenas" in text or "buen día" in text or "buenas tardes" in text or "buenas noches" in text or "inicio" in text):
            print(f"⚠️ Usuario {number} no tiene sesión activa y no envió palabra de inicio")
            return  # Salir sin procesar
    
    # Actualizar timestamp de actividad solo si ya existe sesión
    if number in user_sessions:
        user_sessions[number]['last_active'] = time.time()
    
    # Verificar si el usuario ya ha iniciado sesión se activa con la palabra "hola", hello, hi o opciones
    if "hola" in text or "hello" in text or "hi" in text or "buenas" in text or "buenos día" in text or "buenas tardes" in text or "buenas noches" in text or "inicio" in text:
        
        # Crear o reiniciar sesión SOLO cuando el usuario envía palabra de inicio
        if number not in user_sessions:
            # Crear nueva sesión
            user_sessions[number] = {
                'last_active': time.time(),
                'estado': 'nueva_sesion'
            }
            print(f"🆕 Nueva sesión creada para {number}")
        else:
            # Si ya existe una sesión, reiniciarla
            reiniciar_sesion(number)
        
        # Enviar mensajes de bienvenida (tanto para sesiones nuevas como reiniciadas)
        mensaje = [
        "👋 !Bienvenido al reporte de novedades operacionales de *CHEC*!",
            ]
        enviar_mensajes_con_espera(mensaje, number, espera=2)
        mensaje = [
        "Te invitamos a reportar peligros, amenazas, incidentes, errores operacionales, actos o condiciones inseguras o cualquier otra condición que identifiques para proteger tu seguridad, salud y bienestar de tus compañeros y la de la Empresa. 🚨⚡🚧⚠️",
            ]
        enviar_mensajes_con_espera(mensaje, number, espera=6)
        mensaje = [
        "Este reporte es *CONFIDENCIAL*  y será utilizado únicamente para efectos de prevención y de mejora. Muchas gracias por tu aporte a la seguridad. 👍"
            ]
        enviar_mensajes_con_espera(mensaje, number, espera=4)
        mensaje = [
        "⚠️ Para tu información, la sesión se cerrará automáticamente después de 5 minutos de inactividad."
            ]
        enviar_mensajes_con_espera(mensaje, number, espera=2)
        user_sessions[number]['last_active'] = time.time()

        # # Consulta el nombre del usuario por su número de teléfono
        nombre = buscar_usuario.BuscarNombrexTelefono(number)
        # Si la función retorna un string:
        if nombre:
            user_sessions[number]['nombrereportante'] = nombre[0]
            user_sessions[number]['cedulareportante'] = nombre[1]
            user_sessions[number]['usuarioreportante'] = nombre[2]
            mensaje_nombre = [f"!Bienvenido de nuevo! 😊 \n*{nombre[0]}*"]
            enviar_mensajes_con_espera(mensaje_nombre, number, espera=3)
            # Solo aquí envía la lista de opciones
            whatsappservice.SendMessageWhatsApp(util.ListTipo(number))
        else:
            mensaje_nombre = ["¡Por favor!, indícame tu *Nombre y Apellidos completos* para validar tu nombre:"]
            user_sessions[number]['esperando'] = 'nombre_nuevo'
            enviar_mensajes_con_espera(mensaje_nombre, number, espera=3)
            nuevo= True
            # NO envíes la lista de opciones aquí, espera a que el usuario escriba el nombre y lo valides
                
    elif user_sessions[number].get('esperando') == 'nombre_nuevo':
        nombre = text
        resultados = leer_archivos.buscar_por_nombre(nombre)
        if len(resultados) == 1:
            user_sessions[number]['nombrereportante'] = resultados[0]['nombre']
            user_sessions[number]['cedulareportante'] = resultados[0]['cedula']
            user_sessions[number]['usuarioreportante'] = resultados[0]['usuario']
            mensaje = [f"✅ Bienvenido!: 😊 \n*{resultados[0]['nombre']}*"]
            enviar_mensajes_con_espera(mensaje, number, espera=2)
            # Aquí sí llamas la lista de opciones
            whatsappservice.SendMessageWhatsApp(util.ListTipo(number))
            user_sessions[number].pop('esperando', None)
            return

    # --- FLUJO DE SELECCIÓN DE QUIÉN AFECTA --- 
    elif text.strip() == "me afecta":
        user_sessions[number]['afecta'] = "a mi"
        user_sessions[number]['nombrereportado'] = user_sessions[number].get('nombrereportante', '')
        user_sessions[number]['cedulareportado'] = user_sessions[number].get('cedulareportante', '')
        user_sessions[number]['usuarioreportado'] = user_sessions[number].get('usuarioreportante', '')
        whatsappservice.SendMessageWhatsApp(util.ListTiempo(number))
        return
        # afecta = "a mí"
        # #Menú para seleccionar fecha novedad
        # whatsappservice.SendMessageWhatsApp(util.ListMessage1(number))
    elif text.strip() == "afecta a una persona":
        user_sessions[number]['afecta'] = "a otra persona"
        mensaje = ["¡Por favor!, ¿Cuál es el *Nombre y Apellidos completos* de la persona para quien haces el reporte?"]
        user_sessions[number]['esperando'] = 'nombre_manual'
        enviar_mensajes_con_espera(mensaje, number, espera=3)
        return
        # afecta= "una persona"
        # mensaje_otra_persona = ["¡Por favor!, ¿Cuál es el *Nombre y Apellidos completos* de la persona para quien haces el reporte?"]
        # user_sessions[number]['esperando'] = 'nombre_manual'
        # enviar_mensajes_con_espera(mensaje_otra_persona, number, espera=3)

    elif text.strip() == "afecta a varias personas":
        user_sessions[number]['afecta'] = "varias personas"
        # Pregunta si la novedad afecta a personas o activos
        whatsappservice.SendMessageWhatsApp(util.ListSeguridad(number))
        user_sessions[number]['esperando'] = 'tipo_seguridad'
        return
    
    elif user_sessions[number].get('esperando') == 'tipo_seguridad':
        # El usuario responde si es "Seguridad en personas" o "Seguridad en activos"
        respuesta = text.strip().lower()
        if "personas" in respuesta:
            user_sessions[number]['nombrereportado'] = "Seguridad en personas"
            user_sessions[number]['cedulareportado'] = "0"
            user_sessions[number]['usuarioreportado'] = "0"
        elif "activos" in respuesta:
            user_sessions[number]['nombrereportado'] = "Seguridad en activos"
            user_sessions[number]['cedulareportado'] = "0"
            user_sessions[number]['usuarioreportado'] = "0"
        else:
            whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, selecciona una opción válida: Seguridad en personas o Seguridad en activos.", number))
            return
        # Redirige a pedir la fecha
        whatsappservice.SendMessageWhatsApp(util.ListTiempo(number))
        user_sessions[number].pop('esperando', None)
        return

# --- FLUJO DE CAPTURA DE NOMBRE PARA "AFECTA A UNA PERSONA" ---
    elif user_sessions[number].get('esperando') == 'nombre_manual':
        nombre = text
        resultados = leer_archivos.buscar_por_nombre(nombre)
        if len(resultados) == 0:
            user_sessions[number]['nombrereportado'] = nombre  # Guarda el nombre ingresado
            mensaje = ["❌ No se encontró ninguna persona registrada con ese nombre."]
            enviar_mensajes_con_espera(mensaje, number, espera=2)
            whatsappservice.SendMessageWhatsApp(util.Buttonsningunapersona(number))
            user_sessions[number]['esperando'] = 'manual'
            user_sessions[number].pop('opciones_nombres', None)
        elif len(resultados) == 1:
            user_sessions[number]['nombrereportado'] = resultados[0]['nombre']
            user_sessions[number]['cedulareportado'] = resultados[0]['cedula']
            user_sessions[number]['usuarioreportado'] = resultados[0]['usuario']
            #mensaje = [f"¡La persona es:¡ \n*{resultados[0]['nombre']}*, tu cédula es *{resultados[0]['cedula']}* y tu usuario es *{resultados[0]['usuario']}*."]
            mensaje = [f"✅ La persona es: \n*{resultados[0]['nombre']}*"]
            enviar_mensajes_con_espera(mensaje, number, espera=2)
                        
            user_sessions[number].pop('esperando', None)
            # Ahora, según el valor de afecta, envía el menú correspondiente
            afecta = user_sessions[number].get('afecta')
            if afecta == "a mi":
                whatsappservice.SendMessageWhatsApp(util.ListTipo(number))
            elif afecta == "a otra persona":
                whatsappservice.SendMessageWhatsApp(util.ListTiempo(number))
            elif afecta == "varias personas":
                whatsappservice.SendMessageWhatsApp(util.ListMessage3(number))
        else:
            # Hay varias coincidencias, muestra la lista
            nombres = "\n".join([f"*{i+1}*. {r['nombre']}" for i, r in enumerate(resultados)])
            mensaje = (
                f"⚠️ Se encontraron varias personas que coinciden con tu búsqueda:\n\n{nombres}\n"
                f"*{len(resultados)+1}*. *Ninguno de los anteriores*\n"
                f"\n"
                "Por favor, responde con el número correspondiente al nombre que vas a elegir."
            )
            whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje, number))
            user_sessions[number]['esperando'] = 'seleccion_nombre'
            user_sessions[number]['opciones_nombres'] = [r['nombre'] for r in resultados]
        return

# --- FLUJO DE SELECCIÓN DE NOMBRE SI HAY VARIAS COINCIDENCIAS ---
    elif user_sessions[number].get('esperando') == 'seleccion_nombre':
        try:
            seleccion = int(text.strip())
            opciones = user_sessions[number]['opciones_nombres']
            if 1 <= seleccion <= len(opciones):
                nombre_elegido = opciones[seleccion-1]
                print(f"Nombre elegido: {nombre_elegido}")
                # Aquí puedes buscar el nombre en tu base de datos o lista      
                resultados = leer_archivos.buscar_por_nombre(nombre_elegido)
    
                user_sessions[number]['nombrereportado'] = resultados[0]['nombre']
                user_sessions[number]['cedulareportado'] = resultados[0]['cedula']
                user_sessions[number]['usuarioreportado'] = resultados[0]['usuario']
                mensaje = [f"✅ La persona es: \n*{resultados[0]['nombre']}*"] 
                #mensaje = [f"¡La persona es:¡ \n*{resultados[0]['nombre']}*, tu cédula es *{resultados[0]['cedula']}* y tu usuario es *{resultados[0]['usuario']}*."] 
                
                enviar_mensajes_con_espera(mensaje, number, espera=2)

                user_sessions[number].pop('esperando', None)
                user_sessions[number].pop('opciones_nombres', None)
                # Según el valor de afecta, envía el menú correspondiente
                afecta = user_sessions[number].get('afecta')
                if afecta == "a mi":
                    whatsappservice.SendMessageWhatsApp(util.ListTipo(number))
                elif afecta == "a otra persona":
                    whatsappservice.SendMessageWhatsApp(util.ListTiempo(number))
                elif afecta == "varias personas":
                    whatsappservice.SendMessageWhatsApp(util.ListTiempo(number))
            elif seleccion == len(opciones) + 1:
                #whatsappservice.SendMessageWhatsApp(util.TextMessage("¿Deseas volver a buscar, o ingresar los datos manualmente?", number))
                whatsappservice.SendMessageWhatsApp(util.Buttonsningunapersona(number))
                user_sessions[number]['esperando'] = 'manual'
                user_sessions[number].pop('opciones_nombres', None)
            else:
                whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, responde con un número válido de la lista.", number))
        except ValueError:
            whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, responde solo con el número de la opción.", number))
        return

###  VALIDACION PARA CUANDO NO SE ENCUENTRA NOMBRE EN LA BASE DE DATOS
    elif text.strip() == "volver a buscar":
        whatsappservice.SendMessageWhatsApp(util.TextMessage("¡Por favor!, escribe de nuevo el *Nombre y Apellidos completos* de la persona para quien haces el reporte:", number))
        user_sessions[number]['esperando'] = 'nombre_manual'
        enviar_mensajes_con_espera(mensaje, number, espera=3)
        return

    elif text.strip() == "ingresar manualmente":
        whatsappservice.SendMessageWhatsApp(util.TextMessage("🔢 Escribe la *Cédula* de la persona (7 a 10 dígitos):", number))
        user_sessions[number]['esperando'] = 'cedula_manual_registro'
        return
    # Cuando se pide la cédula manualmente
    elif user_sessions[number].get('esperando') == 'cedula_manual_registro':
        cedula = text.strip()
        if not cedula.isdigit() or not (7 <= len(cedula) <= 10):
            whatsappservice.SendMessageWhatsApp(util.TextMessage("❌ La cédula debe contener entre *7 y 10 dígitos numéricos*. Intenta nuevamente.", number))
            return
        user_sessions[number]['cedulareportado'] = cedula
        whatsappservice.SendMessageWhatsApp(util.TextMessage("📱 Escribe el número de *Teléfono* de la persona (7 a 10 dígitos):", number))
        user_sessions[number]['esperando'] = 'usuario_manual_registro'
        return

    # Cuando se pide el teléfono manualmente y se muestra el resumen
    elif user_sessions[number].get('esperando') == 'usuario_manual_registro':
        telefono = text.strip()
        if not telefono.isdigit() or not (7 <= len(telefono) <= 10):
            whatsappservice.SendMessageWhatsApp(util.TextMessage("❌ El número de teléfono debe tener entre *7 y 10 dígitos*. Intenta nuevamente.", number))
            return
        user_sessions[number]['usuarioreportado'] = telefono
        user_sessions[number].pop('esperando', None)

        # Mostrar resumen de datos registrados
        nombre = user_sessions[number].get('nombrereportado', '').upper()
        cedula = user_sessions[number].get('cedulareportado', '')
        telefono = user_sessions[number].get('usuarioreportado', '')
        resumen = f"✅ *Datos ingresados:*\n📌 Nombre: *{nombre}*\n🪪 Cédula: *{cedula}*\n📞 Teléfono: *{telefono}*"
        whatsappservice.SendMessageWhatsApp(util.TextMessage(resumen, number))

        # Continúa el flujo normal, por ejemplo, pedir la fecha
        whatsappservice.SendMessageWhatsApp(util.ListTiempo(number))
        return
 
## CONDICIONES PARA LA FECHA DE LA NOVEDAD
# --- FLUJO DE SELECCIÓN DE FECHA DE NOVEDAD ---
    elif text.strip() == "hoy":
        user_sessions[number]['fechanovedad'] = fechahoy.strftime("%d-%m-%Y")
        preguntar_municipio(number) 

    elif text.strip() == "ayer":
        user_sessions[number]['fechanovedad'] = (fechahoy - timedelta(days=1)).strftime("%d-%m-%Y")
        # Preguntar municipio
        preguntar_municipio(number)

    elif text.strip() == "antier":
        user_sessions[number]['fechanovedad'] = (fechahoy - timedelta(days=2)).strftime("%d-%m-%Y")
        # Preguntar municipio
        preguntar_municipio(number)

    elif text.strip() == "otra fecha":
        # Pide al usuario que escriba la fecha manualmente
        whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, escribe la fecha en formato DD-MM-YYYY: (ejemplo: 23-07-2025)", number))
        user_sessions[number]['esperando'] = 'fecha_manual'

    elif user_sessions[number].get('esperando') == 'fecha_manual':
        try:
            # Intenta convertir el texto a una fecha válida
            fecha = datetime.strptime(text, "%d-%m-%Y").date()
            user_sessions[number]['fechanovedad'] = fecha.strftime("%d-%m-%Y")  # Guarda en formato estándar
            # Continúa el flujo preguntando el municipio
            preguntar_municipio(number)
            #user_sessions[number].pop('esperando', None)
        except ValueError:
            whatsappservice.SendMessageWhatsApp(util.TextMessage("Formato inválido. Por favor, escribe la fecha en formato DD-MM-YYYY (ejemplo: 23-07-2025):", number))
        
 

    elif user_sessions[number].get('esperando') == 'municipio':
        user_sessions[number]['municipio'] = text.title()
        # Puedes seguir pidiendo más datos aquí, por ejemplo:
        preguntar_lugar(number)
 
    elif user_sessions[number].get('esperando') == 'lugar':
        user_sessions[number]['lugar'] = text.title()
        
        # Mostrar resumen de datos registrados
        datos_usuario = user_sessions[number]
        fecha_hora_actual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
       #resumen = (
        print(
            f"✅ *Resumen de tu reporte:*\n"
            f"• Celular: {number}\n"
            f"• Nombre reportante: {datos_usuario.get('nombrereportante', 'No registrado')}\n"
            f"• Cédula: {datos_usuario.get('cedulareportante', 'No registrada')}\n"
            f"• Usuario: {datos_usuario.get('usuarioreportante', 'No registrado')}\n"
            f"• Nombre reportado: {datos_usuario.get('nombrereportado', 'No registrado')}\n"
            f"• Cédula reportado: {datos_usuario.get('cedulareportado', 'No registrada')}\n"
            f"• Usuario reportado: {datos_usuario.get('usuarioreportado', 'No registrado')}\n"
            f"• Fecha Novedad: {datos_usuario.get('fechanovedad', 'No registrada')}\n"
            f"• Fecha y hora del reporte: {fecha_hora_actual}\n"
            f"• Municipio: {datos_usuario.get('municipio', 'No registrado')}\n"
            f"• Lugar: {datos_usuario.get('lugar', 'No registrado')}\n"
        )
        #whatsappservice.SendMessageWhatsApp(util.TextMessage(resumen, number))
        
        # Puedes seguir pidiendo más datos aquí, por ejemplo:
        preguntar_nota_de_voz(number)
 

 ####  CAPTURAR NOTA DE VOZ Y GUARDAR DATOS EN LA BASE DE DATOS
    elif user_sessions[number].get('esperando') == 'nota_de_voz':
        # Verificar si hay un archivo adjunto en la sesión
        archivo_adjunto = None
        tipo_archivo = user_sessions[number].get('tipo_archivo')
        
        if tipo_archivo:
            if tipo_archivo == 'nota_voz':
                archivo_adjunto = user_sessions[number].get('nota_voz_descargada')
            elif tipo_archivo == 'audio':
                archivo_adjunto = user_sessions[number].get('audio_descargado')
            elif tipo_archivo == 'imagen':
                archivo_adjunto = user_sessions[number].get('imagen_descargada')
            elif tipo_archivo == 'video':
                archivo_adjunto = user_sessions[number].get('video_descargado')
            elif tipo_archivo == 'documento':
                archivo_adjunto = user_sessions[number].get('documento_descargado')
        
        # Usar texto del mensaje o información del archivo
        if archivo_adjunto:
            info_archivo = archivos_adjuntos.obtener_info_archivo(archivo_adjunto)
            descripcion_archivo = f"Archivo {tipo_archivo}: {os.path.basename(archivo_adjunto)}"
            if info_archivo:
                descripcion_archivo += f" ({info_archivo['tamaño_mb']} MB)"
            user_sessions[number]['nota_de_voz'] = descripcion_archivo
        else:
            user_sessions[number]['nota_de_voz'] = text
        
        # Finalizar sesión exitosamente (los datos se registrarán automáticamente en BD)
        finalizar_sesion_exitosa(number)
        return

# --- FLUJO DE VALIDACIÓN DE TRANSCRIPCIÓN DE AUDIO ---
    elif user_sessions[number].get('esperando') == 'validar_transcripcion':
        if text.strip() == "estoy de acuerdo":
            # Usuario confirma la transcripción
            texto_transcrito = user_sessions[number].get('texto_transcrito', '')
            if texto_transcrito:
                # Usar el texto transcrito como nota de voz
                user_sessions[number]['nota_de_voz'] = texto_transcrito
                
                # Limpiar archivos temporales
                audio_file = user_sessions[number].get('audio_descargado') or user_sessions[number].get('nota_voz_descargada')
                wav_file = user_sessions[number].get('audio_wav')
                if audio_file and wav_file:
                    archivos_adjuntos.limpiar_archivos_audio_temporales(audio_file, wav_file)
                
                # Limpiar datos temporales de la sesión
                user_sessions[number].pop('audio_wav', None)
                user_sessions[number].pop('texto_transcrito', None)
                user_sessions[number].pop('esperando', None)
                
                # Continuar con el flujo normal
                mensaje = ["✅ Transcripción registrada."]
                enviar_mensajes_con_espera(mensaje, number, espera=2)
                
                
                # mensaje = ["✅ Tienes fotos o videos?"]
                # enviar_mensajes_con_espera(mensaje, number, espera=2)

                # Establecer estado para esperar respuesta sobre fotos/videos
                user_sessions[number]['esperando'] = 'validar_fotosvideos'
                
                whatsappservice.SendMessageWhatsApp(
                    util.ButtonsTienesFotos(number)
                )

               

            else:
                whatsappservice.SendMessageWhatsApp(
                    util.TextMessage("❌ Error: No se encontró la transcripción. Por favor, envía el audio nuevamente.", number)
                )
                user_sessions[number].pop('esperando', None)
            return
            
        elif text.strip() == "volver a enviarla":
            # Usuario quiere enviar el audio nuevamente
            # mensaje = ["🔄 Por favor, envía nuevamente tu nota de voz o audio."]
            # enviar_mensajes_con_espera(mensaje, number, espera=2)
            
            # Limpiar archivos temporales
            audio_file = user_sessions[number].get('audio_descargado') or user_sessions[number].get('nota_voz_descargada')
            wav_file = user_sessions[number].get('audio_wav')
            if audio_file and wav_file:
                archivos_adjuntos.limpiar_archivos_audio_temporales(audio_file, wav_file)
            
            # Limpiar datos temporales de la sesión
            user_sessions[number].pop('audio_wav', None)
            user_sessions[number].pop('texto_transcrito', None)
            user_sessions[number].pop('esperando', None)
            
            # Volver a preguntar por nota de voz
            preguntar_nota_de_voz(number)
            return
        else:
            # Respuesta no válida
            whatsappservice.SendMessageWhatsApp(
                util.TextMessage("Por favor, selecciona una opción válida de la lista.", number)
            )
            return

# --- FLUJO DE VALIDACIÓN SI TIENE FOTOS O VIDEOS---
    elif user_sessions[number].get('esperando') == 'validar_fotosvideos':
        if text.strip() == "si tengo":
            # Establecer estado para esperar archivos adjuntos
            user_sessions[number]['esperando'] = 'esperando_fotosvideos'
            
            mensaje = ["✅ Por favor adjunta máximo 2 fotos y/o 1 video corto de no más de 30 segundos que tengas de evidencia."]#⏰ Tienes 30 segundos para enviar todos los archivos."]
            enviar_mensajes_con_espera(mensaje, number, espera=2)
            
        elif text.strip() == "no tengo":
            # Finalizar sesión exitosamente
            finalizar_sesion_exitosa(number, "✅ Gracias por tu reporte, te esperamos pronto!! 😊")
            
        else:
            # Respuesta no válida
            whatsappservice.SendMessageWhatsApp(
                util.TextMessage("Por favor, selecciona una opción válida: 'Si tengo' o 'No tengo'.", number)
            )

# --- FLUJO PARA FINALIZAR DESPUÉS DE ADJUNTAR ARCHIVOS ---
    elif user_sessions[number].get('esperando') == 'esperando_fotosvideos':
        # Si el usuario envía un mensaje de texto después de adjuntar archivos, finalizar la sesión
        resumen_archivos = generar_resumen_archivos(number)
        
        if "No hay archivos adjuntos" in resumen_archivos:
            # Si no ha adjuntado archivos, recordarle que adjunte fotos/videos
            mensaje = ["📎 Por favor, adjunta las fotos o videos que tengas de evidencia."]
            enviar_mensajes_con_espera(mensaje, number, espera=2)
        else:
            # Si ya adjuntó archivos, finalizar la sesión
            mensaje = [f"✅ {resumen_archivos}. Gracias por tu reporte, te esperamos pronto!! 😊"]
            
            enviar_mensajes_con_espera(mensaje, number, espera=2)
            finalizar_sesion_exitosa(number)

 ##   FUNCION PARA SALIR DEL CHAT
    elif "salir" in text or "exit" in text:
        finalizar_sesion_usuario(number)
        return  
    elif "contacto" in text or "contact center" in text:
        whatsappservice.SendMessageWhatsApp(util.TextMessage("Puedes contactarnos al *Centro de Atención al Cliente* al 123-456-7890.", number))
 
 
    # for item in listData:
    #     whatsappservice.SendMessageWhatsApp(item)
 
    # datos_usuario = user_sessions[number]
    # print(f"Datos del usuario: "
    #       f"\nCelular:{number}:"
    #       f"\nNombre reportante:{datos_usuario['nombrereportante']}"
    #       f"\nCédula: {datos_usuario['cedulareportante']}"
    #       f"\nUsuario: {datos_usuario['usuarioreportante']}"
    #       f"\nNombre reportado: {datos_usuario['nombrereportado']}"
    #       f"\nCédula: {datos_usuario['cedulareportado']}"
    #       f"\nUsuario: {datos_usuario['usuarioreportado']}"
    #       f"\nFecha: {datos_usuario['fecha']}"
    #       f"\nMunicipio: {datos_usuario['municipio']}"
    #       f"\nLugar: {datos_usuario.get('lugar', 'No proporcionada')}")
 
#Metodo para hacer pruebas
def GenerateMessage(text,number):
    #text = "El ususario dijo: " + text
    text = text.lower()
    if "text" in text:
        data = util.TextMessage("text", number)
    if "format" in text:
        data = util.TextFormatMessage(number)
    if "image" in text:
        data = util.ImageMessage(number)
    if "video" in text:
        data = util.VideoMessage(number)
    if "audio" in text:
        data = util.AudioMessage(number)
    if "location" in text:
        data = util.LocationMessage(number)
    if "document" in text:
        data = util.DocumentMessage(number)
 
    if "button" in text:
        data = util.ButtonsMessage(number)
    if "list" in text:
        data = util.ListMessage(number)
 
    whatsappservice.SendMessageWhatsApp(data)
 
 

if(__name__ == '__main__'):   
    #app.run(port=3000, debug=True)
    import logging
    # Desactivar logs del servidor Werkzeug (Flask)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    #app.run(debug=False, use_reloader=False)
    app.run(port=3000, debug=True)
    

 

 # Función para buscar los nombres en caso de que haya multiples coincidencias
    # elif user_sessions[number].get('esperando') == 'nombre_manual':
    #     nombre = text  # El usuario envió su nombre
    #     resultados = leer_archivos.buscar_por_nombre(nombre)
    #     if len(resultados) == 0:
    #         whatsappservice.SendMessageWhatsApp(util.TextMessage("No se encontraron coincidencias. Por favor, verifica el nombre e intenta de nuevo.", number))
    #     elif len(resultados) == 1:
    #         user_sessions[number]['nombre'] = resultados[0]['nombre']
    #         mensaje = [
    #                     f"¡Bienvenido¡ 😊\n*{resultados[0]['nombre']}*",
    #             ]
    #         enviar_mensajes_con_espera(mensaje, number, espera=2)
    #         #whatsappservice.SendMessageWhatsApp(util.TextMessage(f"✅¡Hola, *{resultados[0]['nombre']}*", number))
    #         user_sessions[number]['nombre'] = nombre
    #         user_sessions[number].pop('esperando', None)
    #         #Enviar lista de opciones para quien reportar propio u otra persona
    #         # Ahora, según el valor de afecta, envía el menú correspondiente
    #     afecta = user_sessions[number].get('afecta')
    #     if afecta == "a mi":
    #         whatsappservice.SendMessageWhatsApp(util.ListMessage(number))
    #     elif afecta == "a otra persona":
    #         nombre = text  # El usuario envió su nombre
    #         resultados = leer_archivos.buscar_por_nombre(nombre)
    #         if len(resultados) == 0:
    #             whatsappservice.SendMessageWhatsApp(util.TextMessage("No se encontraron coincidencias. Por favor, verifica el nombre e intenta de nuevo.", number))
    #         elif len(resultados) == 1:
    #             user_sessions[number]['nombre'] = resultados[0]['nombre']
    #             mensaje = [
    #                         f"¡Bienvenido¡ 😊\n*{resultados[0]['nombre']}*",
    #                 ]
    #             enviar_mensajes_con_espera(mensaje, number, espera=2)
    #         whatsappservice.SendMessageWhatsApp(util.ListMessage1(number))
    #     elif afecta == "varias personas":
    #         whatsappservice.SendMessageWhatsApp(util.ListMessage3(number))

    #     else:
    #         # Hay varias coincidencias, muestra la lista
    #         nombres = "\n".join([f"*{i+1}*. {r['nombre']}" for i, r in enumerate(resultados)])
    #         mensaje = (
    #             f"⚠️ Se encontraron varias personas que coinciden con tu búsqueda:\n\n{nombres}\n"
    #             f"*{len(resultados)+1}*. *Ninguno de los anteriores*\n"
    #             f"\n"
    #             "Por favor, responde con el número correspondiente a tu nombre."
    #         )
    #         whatsappservice.SendMessageWhatsApp(util.TextMessage(mensaje, number))
    #         user_sessions[number]['esperando'] = 'seleccion_nombre'
    #         user_sessions[number]['opciones_nombres'] = [r['nombre'] for r in resultados]
    #         return
       
    # elif user_sessions[number].get('esperando') == 'seleccion_nombre':
    #     try:
    #         seleccion = int(text.strip())
    #         opciones = user_sessions[number]['opciones_nombres']
    #         if 1 <= seleccion <= len(opciones):
    #             nombre_elegido = opciones[seleccion-1]
    #             user_sessions[number]['nombre'] = nombre_elegido
    #             mensaje = [
    #                     f"¡Bienvenido¡ 😊\n*{nombre_elegido}*",
    #             ]
    #             enviar_mensajes_con_espera(mensaje, number, espera=2)                
    #             user_sessions[number].pop('esperando', None)
    #             user_sessions[number].pop('opciones_nombres', None)
    #             #Enviar la lista de opciones para quien reportar propio u otra persona
    #             whatsappservice.SendMessageWhatsApp(util.ListMessage(number))
    #         elif seleccion == len(opciones) + 1:
    #             whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, escribe tu nombre completo para buscar nuevamente.", number))
    #             user_sessions[number]['esperando'] = 'nombre_manual'
    #             user_sessions[number].pop('opciones_nombres', None)
    #         else:
    #             whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, responde con un número válido de la lista.", number))
    #     except ValueError:
    #         whatsappservice.SendMessageWhatsApp(util.TextMessage("Por favor, responde solo con el número de la opción.", number))
    #     return

