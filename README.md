# 🤖 WhatsApp Bot - Node.js

Bot de WhatsApp para reportes de novedades operacionales de CHEC, convertido a Node.js con Express.

## 🚀 Características

- ✅ **Gestión de sesiones** con timeout automático
- ✅ **Rate limiting** para prevenir spam
- ✅ **Descarga de archivos** (audio, imagen, video, documentos, notas de voz)
- ✅ **Validación de datos** robusta
- ✅ **Logging estructurado** con timestamps
- ✅ **API REST** para administración
- ✅ **Manejo de errores** completo
- ✅ **Seguridad** con Helmet y CORS

## 📋 Requisitos

- Node.js >= 16.0.0
- npm o yarn
- Token de WhatsApp Business API

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd whatsapp-bot-nodejs
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp env.example .env
```

Editar `.env` con tus credenciales:
```env
# Configuración de WhatsApp API
WHATSAPP_ACCESS_TOKEN=tu_token_de_whatsapp_aqui
WHATSAPP_API_URL=https://graph.facebook.com/v19.0

# Configuración del servidor
PORT=5000
NODE_ENV=development

# Configuración de sesiones
SESSION_TIMEOUT_MINUTES=5
MAX_REQUESTS_PER_MINUTE=60

# Configuración de archivos
UPLOAD_FOLDER=archivos_descargados
MAX_FILE_SIZE_MB=16
```

4. **Iniciar la aplicación**
```bash
# Desarrollo
npm run dev

# Producción
npm start
```

## 🏗️ Estructura del Proyecto

```
whatsapp-bot-nodejs/
├── app.js                 # 🚀 Aplicación principal
├── config.js              # ⚙️ Configuración centralizada
├── package.json           # 📦 Dependencias
├── .env                   # 🔐 Variables de entorno
├── env.example            # 📝 Ejemplo de variables
├── README.md              # 📖 Documentación
├── utils/                 # 🛠️ Utilidades
│   ├── logger.js          # 📝 Sistema de logging
│   └── validator.js       # ✅ Validaciones
└── services/              # 🔧 Servicios
    ├── sessionManager.js  # 👥 Gestión de sesiones
    ├── rateLimiter.js     # ⏱️ Rate limiting
    ├── messageProcessor.js # 💬 Procesamiento de mensajes
    ├── fileManager.js     # 📁 Gestión de archivos
    └── whatsappService.js # 📱 Servicio de WhatsApp
```

## 🌐 Endpoints

### **Webhook de WhatsApp**
- `GET /whatsapp` - Verificación de token
- `POST /whatsapp` - Recepción de mensajes

### **Administración**
- `GET /welcome` - Página de bienvenida
- `POST /admin/limpiar-sesiones` - Limpiar sesiones expiradas
- `GET /admin/estado-sesiones` - Estado de sesiones activas
- `GET /admin/archivos` - Listar archivos descargados
- `GET /admin/archivos/:filename` - Descargar archivo específico
- `GET /admin/stats` - Estadísticas del sistema

## 🔧 Configuración

### **Variables de Entorno**

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `WHATSAPP_ACCESS_TOKEN` | Token de WhatsApp API | - |
| `WHATSAPP_API_URL` | URL de la API de WhatsApp | `https://graph.facebook.com/v19.0` |
| `PORT` | Puerto del servidor | `5000` |
| `NODE_ENV` | Ambiente de ejecución | `development` |
| `SESSION_TIMEOUT_MINUTES` | Timeout de sesiones | `5` |
| `MAX_REQUESTS_PER_MINUTE` | Límite de requests | `60` |
| `UPLOAD_FOLDER` | Directorio de archivos | `archivos_descargados` |
| `MAX_FILE_SIZE_MB` | Tamaño máximo de archivo | `16` |

## 📱 Flujo de Mensajes

### **1. Mensaje de Texto**
```
Usuario → WhatsApp → Webhook → Procesamiento → Respuesta
```

### **2. Archivo Adjunto**
```
Usuario → WhatsApp → Webhook → Descarga → Confirmación
```

### **3. Estados de Sesión**
```
INITIAL → WAITING_NAME_NEW → WAITING_NAME_MANUAL → 
WAITING_SELECTION → WAITING_CEDULA → WAITING_PHONE → 
WAITING_SECURITY_TYPE → WAITING_DATE_MANUAL → 
WAITING_MUNICIPIO → WAITING_LUGAR → WAITING_VOICE_NOTE
```

## 📁 Gestión de Archivos

### **Tipos Soportados**
- 🎵 **Audio** (.mp3)
- 🖼️ **Imagen** (.jpg, .png, .gif)
- 🎥 **Video** (.mp4, .avi, .mov)
- 📄 **Documento** (.pdf, .doc, .txt)
- 🎤 **Nota de Voz** (.ogg)

### **Convención de Nombres**
```
{tipo}_{numero_usuario}_{timestamp}.{extension}
```

**Ejemplos:**
- `audio_1234567890_20250728_201102.mp3`
- `imagen_1234567890_20250728_201105.jpg`
- `video_1234567890_20250728_201108.mp4`

## 🔒 Seguridad

### **Rate Limiting**
- 100 requests por IP cada 15 minutos
- 60 requests por usuario cada minuto

### **Validaciones**
- ✅ Números de teléfono (7-10 dígitos)
- ✅ Cédulas (7-10 dígitos)
- ✅ Fechas (formato DD-MM-YYYY)
- ✅ Sanitización de texto

### **Middleware de Seguridad**
- Helmet (headers de seguridad)
- CORS configurado
- Rate limiting
- Validación de entrada

## 📊 Logging

### **Niveles de Log**
- ℹ️ **INFO** - Información general
- ✅ **SUCCESS** - Operaciones exitosas
- ⚠️ **WARNING** - Advertencias
- ❌ **ERROR** - Errores
- 🔍 **DEBUG** - Información de debugging (solo desarrollo)

### **Ejemplo de Log**
```
[2025-07-28 20:11:02] ℹ️ INFO: Webhook recibido
[2025-07-28 20:11:03] ✅ SUCCESS: Mensaje enviado a 1234567890
```

## 🚀 Comandos

### **Desarrollo**
```bash
npm run dev          # Iniciar con nodemon
npm run test         # Ejecutar tests
```

### **Producción**
```bash
npm start            # Iniciar aplicación
npm run build        # Construir para producción
```

## 📈 Monitoreo

### **Estadísticas del Sistema**
```bash
curl http://localhost:5000/admin/stats
```

**Respuesta:**
```json
{
  "status": "success",
  "stats": {
    "sesiones_activas": 5,
    "archivos_descargados": 12,
    "rate_limit_stats": {},
    "uptime": 3600,
    "memory_usage": {...},
    "node_version": "v18.0.0",
    "platform": "linux"
  }
}
```

### **Estado de Sesiones**
```bash
curl http://localhost:5000/admin/estado-sesiones
```

### **Listar Archivos**
```bash
curl http://localhost:5000/admin/archivos
```

## 🔧 Desarrollo

### **Estructura de Clases**

#### **SessionManager**
- Gestión de sesiones de usuario
- Timeout automático
- Limpieza de sesiones expiradas

#### **RateLimiter**
- Control de rate limiting por usuario
- Limpieza automática de requests antiguos

#### **MessageProcessor**
- Procesamiento de mensajes según estado
- Manejo de flujo de conversación

#### **FileManager**
- Descarga de archivos adjuntos
- Gestión de directorios
- Información de archivos

#### **WhatsAppService**
- Envío de mensajes a WhatsApp
- Manejo de listas y botones
- Confirmaciones automáticas

### **Agregar Nuevos Estados**

1. **Agregar handler en `MessageProcessor`**
```javascript
async handleNuevoEstado(text, number, session) {
    // Lógica del nuevo estado
}
```

2. **Registrar en el mapeo de handlers**
```javascript
this.handlers = {
    // ... otros handlers
    'NUEVO_ESTADO': this.handleNuevoEstado.bind(this)
};
```

3. **Actualizar transiciones de estado**
```javascript
this.sessionManager.updateSession(number, { state: 'NUEVO_ESTADO' });
```

## 🐛 Troubleshooting

### **Error: Token inválido**
- Verificar `WHATSAPP_ACCESS_TOKEN` en `.env`
- Asegurar que el token sea válido y tenga permisos

### **Error: Archivo no descargado**
- Verificar permisos del directorio `archivos_descargados`
- Revisar logs para errores de red
- Verificar límites de tamaño de archivo

### **Error: Sesiones no se limpian**
- Verificar configuración de `SESSION_TIMEOUT_MINUTES`
- Revisar logs de limpieza automática

### **Error: Rate limit excedido**
- Aumentar `MAX_REQUESTS_PER_MINUTE` si es necesario
- Revisar logs para identificar patrones de spam

## 📝 Changelog

### **v1.0.0**
- ✅ Conversión completa de Python a Node.js
- ✅ Sistema de sesiones con timeout
- ✅ Rate limiting
- ✅ Descarga de archivos adjuntos
- ✅ API de administración
- ✅ Logging estructurado
- ✅ Validaciones robustas
- ✅ Manejo de errores completo

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- 📧 Email: soporte@tuempresa.com
- 📱 WhatsApp: +57 123 456 7890
- 🌐 Web: https://tuempresa.com/soporte

---

**¡Disfruta usando el bot de WhatsApp! 🎉** 