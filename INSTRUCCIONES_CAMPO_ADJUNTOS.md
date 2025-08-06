# Instrucciones para Agregar Campo Adjuntos

## Cambios Realizados

Se ha modificado el sistema para separar la información de archivos adjuntos del texto del reporte, creando un campo independiente llamado `adjuntos` en la base de datos.

## Pasos para Implementar

### 1. Ejecutar Script SQL
Ejecutar el archivo `agregar_campo_adjuntos.sql` en la base de datos:

```sql
-- Reemplazar [tu_base_de_datos] con el nombre real de la base de datos
USE [tu_base_de_datos];

-- Agregar el campo adjuntos
ALTER TABLE dbo.REPORTE_NOVEDADES 
ADD adjuntos NVARCHAR(MAX) NULL;
```

### 2. Archivos Modificados

#### `Funciones_bd/insertar_bd_azure.py`
- ✅ Agregado campo `adjuntos` en la consulta INSERT
- ✅ Agregado parámetro `adjuntos` en la ejecución

#### `app.py`
- ✅ Modificada función `registrar_datos_en_bd()` para separar adjuntos del texto
- ✅ Campo `textoreporte` ahora solo contiene la transcripción de audio
- ✅ Campo `adjuntos` contiene la información de archivos adjuntos

## Estructura de Datos

### Campo `textoreporte`
- **Contenido**: Solo la transcripción de audio/nota de voz
- **Ejemplo**: "El usuario reportó un incidente en la calle principal..."

### Campo `adjuntos`
- **Contenido**: Lista de archivos adjuntos con información detallada
- **Ejemplo**:
```
• Imagen 1: imagen_573001234567_20241201_143022.jpg (2.5 MB)
• Video 1: video_573001234567_20241201_143025.mp4 (15.2 MB)
• Documento 1: documento_573001234567_20241201_143030.pdf (1.8 MB)
```

## Beneficios

1. **Separación clara**: El texto del reporte y los adjuntos están separados
2. **Mejor organización**: Facilita el análisis y búsqueda de información
3. **Escalabilidad**: Permite agregar más tipos de adjuntos en el futuro
4. **Compatibilidad**: Mantiene la funcionalidad existente

## Verificación

Después de implementar los cambios:

1. Verificar que el campo `adjuntos` existe en la tabla
2. Probar el envío de archivos adjuntos
3. Confirmar que se guardan correctamente en campos separados
4. Verificar que el texto del reporte solo contiene la transcripción

## Notas Importantes

- El campo `adjuntos` es opcional (NULL permitido)
- Los archivos físicos se siguen eliminando al finalizar la sesión
- La información de adjuntos se mantiene en la base de datos para referencia 