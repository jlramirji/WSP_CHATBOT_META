import os
import codecs
from datetime import datetime

# Funcion para escribir el log de ejecucion de insercion
def escribir(log_file_, mensaje_):
    try:
        # Verificar si la carpeta existe
        log_dir = os.path.dirname(log_file_)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)  # Crear la carpeta si no existe
            print(f" Carpeta creada: {log_dir}")
        
        # Escribir el mensaje en el archivo de log
        with codecs.open(log_file_, mode='a', encoding='utf-8') as file:
            file.write(mensaje_ + "\n")
        return 'Insercion del mensaje en el log ha sido exitosa'
    except Exception as e:
        # Manejar el error y continuar la ejecucion
        print(f" Error al escribir en el archivo de log: {e}")
        return 'Error al escribir en el log'

def generar_nombre_log_chat(numero_telefono):
    """
    Genera el nombre del archivo de log para una sesión de chat específica
    
    Args:
        numero_telefono (str): Número de teléfono del usuario
    
    Returns:
        str: Nombre del archivo de log con formato chat_whatsapp_[numero]_[fecha]
    """
    fecha_actual = datetime.now().strftime('%d%m%Y')
    # Limpiar el número de teléfono (remover caracteres especiales)
    numero_limpio = ''.join(filter(str.isdigit, str(numero_telefono)))
    return f"logs/chat_whatsapp_{numero_limpio}_{fecha_actual}.log"

def generar_nombre_log_audio(numero_telefono):
    """
    Genera el nombre del archivo de log para procesamiento de audio específico
    
    Args:
        numero_telefono (str): Número de teléfono del usuario
    
    Returns:
        str: Nombre del archivo de log con formato audio_processing_[numero]_[fecha]
    """
    fecha_actual = datetime.now().strftime('%d%m%Y')
    # Limpiar el número de teléfono (remover caracteres especiales)
    numero_limpio = ''.join(filter(str.isdigit, str(numero_telefono)))
    return f"logs/audio_processing_{numero_limpio}_{fecha_actual}.log"

def escribir_log_sesion(numero_telefono, mensaje, tipo_log="CHAT"):
    """
    Escribe en el log específico de la sesión del usuario
    
    Args:
        numero_telefono (str): Número de teléfono del usuario
        mensaje (str): Mensaje a escribir en el log
        tipo_log (str): Tipo de log ("CHAT" o "AUDIO")
    """
    if tipo_log.upper() == "AUDIO":
        log_file = generar_nombre_log_audio(numero_telefono)
    else:
        log_file = generar_nombre_log_chat(numero_telefono)
    
    return escribir(log_file, mensaje)

def crear_mensaje_log(tipo, mensaje, numero_usuario=None, detalles=""):
    """
    Crea un mensaje de log formateado con timestamp
    
    Args:
        tipo (str): Tipo de log (INFO, ERROR, WARNING, CHAT, etc.)
        mensaje (str): Mensaje principal
        numero_usuario (str): Número de teléfono del usuario (opcional)
        detalles (str): Detalles adicionales (opcional)
    
    Returns:
        str: Mensaje formateado para el log
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if numero_usuario:
        log_msg = f"[{timestamp}] [{tipo}] [{numero_usuario}] {mensaje}"
    else:
        log_msg = f"[{timestamp}] [{tipo}] {mensaje}"
    
    if detalles:
        log_msg += f" | {detalles}"
    
    return log_msg

def log_chat_mensaje(numero, tipo_mensaje, contenido, direccion="entrada"):
    """
    Registra mensajes específicos del chat
    
    Args:
        numero (str): Número de teléfono
        tipo_mensaje (str): Tipo de mensaje (texto, audio, imagen, etc.)
        contenido (str): Contenido del mensaje
        direccion (str): Dirección (entrada/salida)
    """
    emoji = "📥" if direccion == "entrada" else "📤"
    mensaje = f"{emoji} {direccion.upper()} {tipo_mensaje.upper()}: {contenido}"
    return crear_mensaje_log("CHAT", mensaje, numero)

def log_sesion_usuario(numero, accion, detalles=""):
    """
    Registra acciones de sesión de usuario
    
    Args:
        numero (str): Número de teléfono
        accion (str): Acción (creada, actualizada, eliminada, etc.)
        detalles (str): Detalles adicionales
    """
    mensaje = f"👤 SESION {accion.upper()}: {detalles}"
    return crear_mensaje_log("SESSION", mensaje, numero)

def log_error(mensaje_error, contexto="", excepcion=None):
    """
    Registra errores
    
    Args:
        mensaje_error (str): Mensaje de error
        contexto (str): Contexto del error
        excepcion (Exception): Excepción si existe
    """
    mensaje = f"❌ ERROR {contexto}: {mensaje_error}"
    if excepcion:
        mensaje += f" | Excepción: {str(excepcion)}"
    return crear_mensaje_log("ERROR", mensaje)

def log_exito(mensaje_exito, contexto=""):
    """
    Registra operaciones exitosas
    
    Args:
        mensaje_exito (str): Mensaje de éxito
        contexto (str): Contexto adicional
    """
    mensaje = f"✅ EXITO {contexto}: {mensaje_exito}"
    return crear_mensaje_log("SUCCESS", mensaje)