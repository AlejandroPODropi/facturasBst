# 📧 Configuración de Gmail API

Esta guía te ayudará a configurar la integración con Gmail API para el procesamiento automático de facturas.

## 🔧 Requisitos Previos

1. **Cuenta de Google** con acceso a Gmail
2. **Proyecto en Google Cloud Console**
3. **Gmail API habilitada**

## 📋 Pasos de Configuración

### 1. Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Gmail API**:
   - Ve a "APIs & Services" > "Library"
   - Busca "Gmail API"
   - Haz clic en "Enable"

### 2. Configurar OAuth 2.0

1. Ve a "APIs & Services" > "Credentials"
2. Haz clic en "Create Credentials" > "OAuth client ID"
3. Selecciona "Desktop application"
4. Descarga el archivo JSON de credenciales
5. Renómbralo a `credentials.json` y colócalo en la raíz del proyecto backend

### 3. Configurar Scopes

Los siguientes scopes son necesarios:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.modify`

### 4. Configurar Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```env
# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.modify
```

## 🚀 Primera Ejecución

### 1. Autenticación Inicial

La primera vez que ejecutes la aplicación:

1. Inicia el servidor backend
2. Ve al dashboard en el frontend
3. Haz clic en "Conectar Gmail"
4. Se abrirá una ventana del navegador para autorizar la aplicación
5. Autoriza el acceso a tu cuenta de Gmail

### 2. Verificar Conexión

Una vez autenticado, verás:
- ✅ Estado: "Conectado a Gmail"
- 📊 Estadísticas de correos recientes
- 🔄 Botón para procesar facturas

## 📊 Funcionalidades Disponibles

### Procesamiento Automático de Facturas

El sistema puede:
- **Buscar correos** con adjuntos de los últimos 7 días
- **Identificar facturas** por palabras clave
- **Extraer datos** automáticamente:
  - Proveedor
  - Monto
  - Fecha
  - Descripción
- **Crear facturas** en el sistema
- **Marcar correos** como leídos

### Palabras Clave de Detección

El sistema busca estas palabras en asunto y cuerpo:
- `factura`, `invoice`
- `recibo`, `comprobante`
- `gasto`, `expense`
- `pago`, `payment`
- `cobro`, `charge`
- `servicio`, `service`

### Tipos de Archivo Soportados

- **PDF** - Para facturas digitales
- **Imágenes** - JPG, PNG para facturas escaneadas
- **Excel/CSV** - Para reportes de gastos

## 🔒 Seguridad

### Permisos Mínimos

La aplicación solo solicita:
- **Lectura de correos** - Para buscar facturas
- **Modificación de etiquetas** - Para marcar como leído

### Datos Sensibles

- Las credenciales se almacenan localmente
- No se almacenan contraseñas
- Solo se accede a correos con adjuntos

## 🛠 Solución de Problemas

### Error: "No se pudo autenticar con Gmail API"

**Causas posibles:**
1. Archivo `credentials.json` no encontrado
2. Gmail API no habilitada
3. Scopes incorrectos

**Soluciones:**
1. Verifica que `credentials.json` esté en la raíz del backend
2. Habilita Gmail API en Google Cloud Console
3. Verifica los scopes en la configuración

### Error: "Access denied"

**Causas posibles:**
1. Usuario no autorizó la aplicación
2. Token expirado

**Soluciones:**
1. Elimina `token.json` y vuelve a autenticar
2. Verifica permisos en Google Cloud Console

### No se detectan facturas

**Causas posibles:**
1. Correos sin palabras clave
2. Sin archivos adjuntos
3. Formato de correo no reconocido

**Soluciones:**
1. Verifica que los correos contengan palabras clave
2. Asegúrate de que tengan adjuntos
3. Revisa el formato del asunto y cuerpo

## 📈 Monitoreo

### Estadísticas Disponibles

- **Total de correos** (últimos 7 días)
- **Correos con adjuntos**
- **Correos no leídos**
- **Tasa de adjuntos**

### Logs

Los logs se encuentran en:
- **Backend**: `backend/logs/gmail.log`
- **Frontend**: Consola del navegador

## 🔄 Mantenimiento

### Renovación de Tokens

Los tokens se renuevan automáticamente. Si hay problemas:
1. Elimina `token.json`
2. Vuelve a autenticar

### Actualización de Credenciales

Si cambias las credenciales:
1. Reemplaza `credentials.json`
2. Elimina `token.json`
3. Vuelve a autenticar

## 📞 Soporte

Para problemas técnicos:
1. Revisa los logs
2. Verifica la configuración
3. Consulta la documentación de Gmail API

## 🎯 Próximos Pasos

Una vez configurado, puedes:
1. **Procesar facturas** automáticamente
2. **Configurar filtros** personalizados
3. **Integrar con OCR** para facturas físicas
4. **Automatizar notificaciones**

---

**¡La integración con Gmail está lista para procesar facturas automáticamente!** 🚀
