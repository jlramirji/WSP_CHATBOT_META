#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de logs específicos por sesión
"""

import sys
import os

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Funciones_py import crear_log
from datetime import datetime

def test_logs_sesion():
    """
    Prueba el sistema de logs específicos por sesión
    """
    print("🧪 Probando sistema de logs específicos por sesión...")
    
    # Número de teléfono de prueba
    numero_prueba = "573137182944"
    
    # Probar generación de nombres de archivos
    print("\n📝 Generando nombres de archivos de log:")
    
    nombre_log_chat = crear_log.generar_nombre_log_chat(numero_prueba)
    nombre_log_audio = crear_log.generar_nombre_log_audio(numero_prueba)
    
    print(f"   Chat log: {nombre_log_chat}")
    print(f"   Audio log: {nombre_log_audio}")
    
    # Probar escritura de logs específicos por sesión
    print("\n✍️ Escribiendo logs de prueba:")
    
    # Log de chat
    mensaje_chat = crear_log.crear_mensaje_log("TEST", "Mensaje de prueba para chat", numero_prueba, "prueba del sistema")
    resultado_chat = crear_log.escribir_log_sesion(numero_prueba, mensaje_chat, "CHAT")
    print(f"   Chat log: {resultado_chat}")
    
    # Log de audio
    mensaje_audio = crear_log.crear_mensaje_log("TEST", "Mensaje de prueba para audio", numero_prueba, "prueba del sistema")
    resultado_audio = crear_log.escribir_log_sesion(numero_prueba, mensaje_audio, "AUDIO")
    print(f"   Audio log: {resultado_audio}")
    
    # Verificar que los archivos se crearon
    print("\n🔍 Verificando archivos creados:")
    
    if os.path.exists(nombre_log_chat):
        print(f"   ✅ Chat log creado: {nombre_log_chat}")
        # Mostrar contenido
        with open(nombre_log_chat, 'r', encoding='utf-8') as f:
            contenido = f.read()
            print(f"   📄 Contenido: {contenido.strip()}")
    else:
        print(f"   ❌ Chat log no encontrado: {nombre_log_chat}")
    
    if os.path.exists(nombre_log_audio):
        print(f"   ✅ Audio log creado: {nombre_log_audio}")
        # Mostrar contenido
        with open(nombre_log_audio, 'r', encoding='utf-8') as f:
            contenido = f.read()
            print(f"   📄 Contenido: {contenido.strip()}")
    else:
        print(f"   ❌ Audio log no encontrado: {nombre_log_audio}")
    
    print("\n🎉 Prueba completada!")

if __name__ == "__main__":
    test_logs_sesion() 