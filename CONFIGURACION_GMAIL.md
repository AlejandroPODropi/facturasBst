# 📧 Configuración Detallada de Gmail API

## 🎯 Objetivo

Esta guía te ayudará a configurar completamente la integración con Gmail API para el procesamiento automático de facturas electrónicas.

---

## 🔧 Requisitos Previos

1. **Cuenta de Google** con acceso a Gmail
2. **Proyecto en Google Cloud Console**
3. **Gmail API habilitada**
4. **Archivo de credenciales OAuth 2.0**

---

## 📋 Pasos de Configuración Detallados

### 1. Crear Proyecto en Google Cloud Console

#### 1.1 Acceder a Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Inicia sesión con tu cuenta de Google
3. Acepta los términos de servicio si es la primera vez

#### 1.2 Crear o Seleccionar Proyecto
1. En la parte superior, haz clic en el selector de proyectos
2. Haz clic en "Nuevo proyecto"
3. Ingresa un nombre para el proyecto (ej: "facturas-boosting")
4. Haz clic en "Crear"

### 2. Habilitar Gmail API

#### 2.1 Navegar a la Biblioteca de APIs
1. En el menú lateral, ve a "APIs y servicios" > "Biblioteca"
2. Busca "Gmail API"
3. Haz clic en "Gmail API" en los resultados

#### 2.2 Habilitar la API
1. Haz clic en "Habilitar"
2. Espera a que se habilite (puede tomar unos minutos)

### 3. Configurar OAuth 2.0

#### 3.1 Crear Credenciales
1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "ID de cliente OAuth"
3. Si es la primera vez, configura la pantalla de consentimiento:
   - Selecciona "Externo"
   - Completa la información requerida
   - Agrega tu email como usuario de prueba

#### 3.2 Configurar ID de Cliente OAuth
1. Selecciona "Aplicación de escritorio"
2. Ingresa un nombre (ej: "Facturas Boosting Desktop")
3. Haz clic en "Crear"

#### 3.3 Descargar Credenciales
1. Se abrirá una ventana con las credenciales
2. Haz clic en "Descargar JSON"
3. Renombra el archivo a `credentials.json`
4. Colócalo en la raíz del proyecto backend

### 4. Configurar Scopes

Los siguientes scopes son necesarios para el funcionamiento completo:

```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.modify
```

Estos scopes permiten:
- **readonly:** Leer correos y adjuntos
- **modify:** Marcar correos como leídos

### 5. Configurar Variables de Entorno

Agrega las siguientes variables a tu archivo `.env` en el directorio `backend/`:

```env
# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.modify
```

---

## 🚀 Primera Ejecución y Autenticación

### 1. Iniciar el Sistema

```bash
# Ejecutar backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Autenticación Inicial

1. Abre el navegador y ve a: http://localhost:8000/docs
2. Busca el endpoint `/gmail/auth/authenticate`
3. Haz clic en "Try it out" y luego "Execute"
4. Se abrirá una ventana del navegador para autorizar la aplicación
5. Selecciona tu cuenta de Google
6. Revisa los permisos solicitados
7. Haz clic en "Permitir"

### 3. Verificar Conexión

```bash
# Verificar estado de autenticación
curl http://localhost:8000/api/v1/gmail/auth/status

# Respuesta esperada:
# {"authenticated": true, "message": "Autenticado con Gmail API"}
```

---

## 📊 Funcionalidades Disponibles

### 1. Procesamiento Automático de Facturas

El sistema puede:
- **Buscar correos** con adjuntos de los últimos 7 días
- **Detectar facturas** por palabras clave
- **Extraer datos** automáticamente (proveedor, monto, fecha)
- **Crear facturas** en el sistema
- **Marcar correos** como leídos

### 2. Endpoints Disponibles

#### Autenticación
- `GET /gmail/auth/status` - Verificar estado de autenticación
- `POST /gmail/auth/authenticate` - Iniciar proceso de autenticación

#### Procesamiento
- `POST /gmail/process-invoices/sync` - Procesar facturas manualmente
- `GET /gmail/emails/search` - Buscar correos específicos
- `GET /gmail/emails/{message_id}` - Obtener detalles de un correo

#### Estadísticas
- `GET /gmail/stats` - Obtener estadísticas de Gmail

### 3. Palabras Clave para Detección

El sistema busca correos que contengan:
- "factura"
- "invoice"
- "comprobante"
- "recibo"
- "bill"

---

## 🔧 Configuración Avanzada

### 1. Personalizar Búsqueda de Correos

Puedes modificar la consulta de búsqueda en `backend/src/services/gmail_service.py`:

```python
# Búsqueda por defecto
query = "has:attachment newer_than:7d"

# Búsqueda personalizada
query = "has:attachment from:proveedor@empresa.com newer_than:30d"
```

### 2. Configurar Procesamiento Automático

Para procesar facturas automáticamente cada cierto tiempo, puedes usar un cron job:

```bash
# Ejemplo: procesar cada hora
0 * * * * curl -X POST http://localhost:8000/api/v1/gmail/process-invoices/sync?limit=10
```

### 3. Filtros de Correos

Puedes agregar filtros adicionales en Gmail para organizar mejor las facturas:

1. Ve a Gmail > Configuración > Filtros y direcciones bloqueadas
2. Crea un filtro para correos con "factura" en el asunto
3. Aplica la etiqueta "Facturas" automáticamente

---

## 🧪 Pruebas y Verificación

### 1. Probar Procesamiento Manual

```bash
# Procesar 5 facturas recientes
curl -X POST "http://localhost:8000/api/v1/gmail/process-invoices/sync?limit=5"
```

### 2. Verificar Estadísticas

```bash
# Obtener estadísticas de Gmail
curl http://localhost:8000/api/v1/gmail/stats
```

### 3. Buscar Correos Específicos

```bash
# Buscar correos con adjuntos
curl "http://localhost:8000/api/v1/gmail/emails/search?query=has:attachment&max_results=10"
```

---

## 🔒 Seguridad y Mejores Prácticas

### 1. Proteger Credenciales

- **Nunca** subas `credentials.json` o `token.json` al repositorio
- Agrega estos archivos a `.gitignore`
- Usa variables de entorno para configuraciones sensibles

### 2. Límites de la API

- **Cuota diaria:** 1,000,000,000 cuotas por día
- **Límite por usuario:** 250 cuotas por usuario por segundo
- **Límite por proyecto:** 1,000 cuotas por segundo

### 3. Monitoreo

- Revisa regularmente los logs del servidor
- Monitorea el uso de cuotas en Google Cloud Console
- Configura alertas para errores de autenticación

---

## 🚨 Solución de Problemas

### Error: "Access blocked: This app's request is invalid"

**Problema:** La aplicación no está verificada por Google.

**Solución:**
1. Ve a Google Cloud Console > APIs y servicios > Pantalla de consentimiento
2. Agrega tu email como usuario de prueba
3. O solicita verificación de la aplicación

### Error: "The OAuth client was not found"

**Problema:** El archivo `credentials.json` no está en la ubicación correcta.

**Solución:**
1. Verifica que `credentials.json` esté en la raíz del proyecto backend
2. Verifica que el archivo no esté corrupto
3. Regenera las credenciales si es necesario

### Error: "Token has been expired or revoked"

**Problema:** El token de acceso ha expirado.

**Solución:**
1. Elimina el archivo `token.json`
2. Ejecuta nuevamente el proceso de autenticación
3. Autoriza la aplicación nuevamente

---

## 📈 Métricas y Monitoreo

### 1. Estadísticas Disponibles

El endpoint `/gmail/stats` proporciona:
- Total de correos en los últimos 7 días
- Correos con adjuntos
- Correos no leídos
- Tasa de adjuntos

### 2. Logs del Sistema

Revisa los logs del servidor para:
- Errores de autenticación
- Problemas de procesamiento
- Estadísticas de uso

### 3. Dashboard de Gmail

En el frontend, puedes ver:
- Estado de conexión con Gmail
- Estadísticas en tiempo real
- Historial de facturas procesadas

---

**¡Integración Gmail API configurada y lista para procesar facturas automáticamente! 🎉**
