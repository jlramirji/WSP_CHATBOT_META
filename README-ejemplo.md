# 🤖 Bot de WhatsApp - Ejemplo Completo

Este es un ejemplo completo de un bot de WhatsApp en Node.js que demuestra cómo manejar una secuencia de conversación, capturar datos del usuario y almacenarlos en una base de datos.

## 🚀 Características

- ✅ **Secuencia de conversación paso a paso**
- ✅ **Manejo de estados de sesión**
- ✅ **Envío de listas interactivas**
- ✅ **Envío de botones**
- ✅ **Validación de datos**
- ✅ **Almacenamiento en base de datos**
- ✅ **Webhook para WhatsApp Business API**
- ✅ **Limpieza automática de sesiones**

## 📋 Flujo de Conversación

1. **Inicio**: Usuario escribe "hola"
2. **Nombre**: Captura del nombre completo
3. **Edad**: Captura de la edad con validación
4. **Ciudad**: Captura de la ciudad
5. **Servicio**: Lista de servicios disponibles
6. **Descripción**: Captura de descripción del requerimiento
7. **Finalización**: Resumen y botones de acción

## 🛠️ Instalación

1. **Clona o descarga los archivos**
2. **Instala las dependencias**:
   ```bash
   npm install
   ```

3. **Configura las variables de entorno**:
   - Copia `env-ejemplo.txt` a `.env`
   - Completa con tus credenciales de WhatsApp Business API

4. **Inicia el servidor**:
   ```bash
   npm start
   # o para desarrollo
   npm run dev
   ```

## 🔧 Configuración de WhatsApp Business API

1. **Obtén tu token de acceso** desde Meta Developer Console
2. **Obtén tu Phone Number ID** desde WhatsApp Business API
3. **Configura el webhook**:
   - URL: `https://tu-dominio.com/webhook`
   - Verify Token: El valor que configuraste en `VERIFY_TOKEN`

## 📱 Endpoints Disponibles

- `GET /webhook` - Verificación del webhook
- `POST /webhook` - Recepción de mensajes
- `GET /test?phone=1234567890` - Envío de mensaje de prueba
- `GET /sessions` - Ver estado de sesiones activas

## 💾 Estructura de Datos Capturados

```javascript
{
  name: "Juan Pérez",
  age: 30,
  city: "Bogotá",
  service: "Consultoría",
  description: "Necesito asesoría para mi proyecto",
  phoneNumber: "573001234567",
  registrationDate: "2024-01-15T10:30:00.000Z"
}
```

## 🔄 Estados de la Conversación

- `INITIAL` - Estado inicial
- `WAITING_NAME` - Esperando nombre
- `WAITING_AGE` - Esperando edad
- `WAITING_CITY` - Esperando ciudad
- `WAITING_SERVICE` - Esperando selección de servicio
- `WAITING_DESCRIPTION` - Esperando descripción
- `COMPLETED` - Conversación completada

## 📊 Funciones Principales

### Envío de Mensajes
- `sendTextMessage()` - Mensajes de texto simples
- `sendListMessage()` - Listas interactivas
- `sendButtonMessage()` - Botones de respuesta

### Gestión de Sesiones
- `initializeSession()` - Crear nueva sesión
- `getSession()` - Obtener sesión existente
- `updateSessionState()` - Actualizar estado
- `finalizeSession()` - Finalizar sesión

### Procesamiento
- `processMessage()` - Procesar mensajes entrantes
- `handleInteractiveMessage()` - Manejar interacciones
- `saveToDatabase()` - Guardar en base de datos

## 🎯 Personalización

### Agregar Nuevos Estados
1. Añade el estado en `STATES`
2. Crea el manejador `handleNewState()`
3. Añade el caso en `processMessage()`

### Modificar el Flujo
1. Edita los manejadores de estado
2. Ajusta las validaciones
3. Modifica los mensajes enviados

### Conectar Base de Datos Real
Reemplaza `saveToDatabase()` con tu lógica de base de datos:

```javascript
async function saveToDatabase(userData) {
  // Ejemplo con PostgreSQL
  const client = await pool.connect();
  try {
    const query = `
      INSERT INTO registrations (name, age, city, service, description, phone_number, created_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id
    `;
    const values = [
      userData.name,
      userData.age,
      userData.city,
      userData.service,
      userData.description,
      userData.phoneNumber,
      userData.registrationDate
    ];
    const result = await client.query(query, values);
    return { success: true, id: result.rows[0].id };
  } finally {
    client.release();
  }
}
```

## 🧪 Pruebas

1. **Mensaje de prueba**:
   ```
   GET http://localhost:3000/test?phone=573001234567
   ```

2. **Ver sesiones activas**:
   ```
   GET http://localhost:3000/sessions
   ```

## 🔒 Seguridad

- ✅ Validación de entrada
- ✅ Timeout de sesiones
- ✅ Limpieza automática
- ✅ Manejo de errores
- ✅ Logs de actividad

## 📝 Logs

El bot genera logs detallados:
- 📨 Mensajes recibidos
- ✅ Mensajes enviados
- 🔄 Cambios de estado
- ⏰ Sesiones expiradas
- ❌ Errores

## 🚀 Despliegue

1. **Heroku**:
   ```bash
   heroku create tu-bot-whatsapp
   git push heroku main
   ```

2. **Vercel**:
   ```bash
   vercel --prod
   ```

3. **Railway**:
   ```bash
   railway login
   railway up
   ```

## 📞 Soporte

Para dudas o problemas:
- Revisa los logs del servidor
- Verifica la configuración de WhatsApp Business API
- Asegúrate de que el webhook esté configurado correctamente

---

**¡Listo para usar! 🎉** 