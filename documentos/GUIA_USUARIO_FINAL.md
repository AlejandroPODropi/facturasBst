# Guía de Usuario - Sistema de Gestión de Facturas

## Introducción

Bienvenido al Sistema de Gestión de Facturas. Esta guía te ayudará a utilizar todas las funcionalidades disponibles para gestionar tus facturas de manera eficiente.

## 🚀 Acceso al Sistema

### URLs del Sistema
- **Aplicación Principal:** [https://frontend-493189429371.us-central1.run.app](https://frontend-493189429371.us-central1.run.app)
- **API Backend:** [https://backend-493189429371.us-central1.run.app](https://backend-493189429371.us-central1.run.app)

### Requisitos
- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Conexión a internet
- Cuenta de Gmail (para integración automática)

## 📱 Interfaz del Sistema

### Navegación Principal
- **Dashboard:** Vista general con estadísticas
- **Facturas:** Gestión completa de facturas
- **Usuarios:** Administración de usuarios (solo administradores)
- **Gmail:** Integración con Gmail para procesamiento automático

### Diseño Responsivo
El sistema se adapta automáticamente a tu dispositivo:
- **Desktop:** Interfaz completa con sidebar fijo
- **Móvil:** Sidebar colapsable con menú hamburguesa

## 📊 Dashboard

### Estadísticas Generales
- **Total de Usuarios:** Número de usuarios registrados
- **Total de Facturas:** Cantidad total de facturas en el sistema
- **Monto Total:** Suma de todos los montos de facturas
- **Facturas Pendientes:** Facturas que requieren revisión

### Gráficos y Tendencias
- **Tendencias de Facturas:** Gráfico de facturas por mes
- **Estadísticas por Usuario:** Distribución de facturas por usuario
- **Métricas de Gmail:** Estadísticas de procesamiento automático

## 📄 Gestión de Facturas

### Crear Factura Manualmente

1. **Acceder a la sección:**
   - Haz clic en "Facturas" en el menú principal
   - Presiona el botón "Nueva Factura"

2. **Subir archivo:**
   - Arrastra y suelta tu archivo PDF o imagen
   - O haz clic en "Seleccionar archivo"
   - Formatos soportados: PDF, JPG, PNG

3. **Revisar datos extraídos:**
   - El sistema procesará automáticamente el archivo con OCR
   - Revisa los datos extraídos:
     - **Proveedor:** Nombre de la empresa
     - **Monto:** Valor de la factura
     - **Fecha:** Fecha de emisión
     - **NIT:** Número de identificación tributaria

4. **Completar información:**
   - **Usuario:** Selecciona el usuario responsable
   - **Método de Pago:** Tarjeta BST, Tarjeta Personal, Efectivo, Transferencia
   - **Categoría:** Alimentación, Transporte, Servicios, Suministros, Mantenimiento, Otros
   - **Descripción:** Información adicional (opcional)

5. **Guardar:**
   - Haz clic en "Crear Factura"
   - La factura se guardará y aparecerá en la lista

### Ver y Filtrar Facturas

1. **Lista de Facturas:**
   - Ve a "Facturas" en el menú principal
   - Verás todas las facturas con paginación (10 por página)

2. **Filtros disponibles:**
   - **Usuario:** Filtra por usuario responsable
   - **Proveedor:** Busca por nombre de proveedor
   - **Fecha:** Rango de fechas
   - **Estado:** Pendiente, Validada, Rechazada
   - **Monto:** Rango de montos

3. **Búsqueda:**
   - Usa el campo de búsqueda para encontrar facturas específicas
   - Busca por proveedor, descripción o NIT

### Editar Factura

1. **Acceder a edición:**
   - En la lista de facturas, haz clic en el ícono de editar
   - O haz clic en el nombre de la factura

2. **Modificar datos:**
   - Cambia cualquier campo necesario
   - Actualiza el estado si es necesario

3. **Guardar cambios:**
   - Haz clic en "Actualizar Factura"
   - Los cambios se aplicarán inmediatamente

### Eliminar Factura

1. **Confirmar eliminación:**
   - Haz clic en el ícono de eliminar
   - Confirma la acción en el diálogo
   - **⚠️ Advertencia:** Esta acción no se puede deshacer

## 📧 Integración con Gmail

### Configurar Gmail

1. **Acceder a la integración:**
   - Ve al Dashboard
   - Busca la sección "Integración Gmail"
   - Haz clic en "Configurar Gmail"

2. **Autorizar acceso:**
   - Se abrirá una ventana de Google
   - Inicia sesión con tu cuenta de Gmail
   - Autoriza el acceso a tu correo

3. **Verificar configuración:**
   - El sistema confirmará la conexión exitosa
   - Verás el estado "Conectado" en el dashboard

### Análisis Automático de Facturas

1. **Iniciar análisis:**
   - En el Dashboard, haz clic en "Analizar Facturas"
   - Se abrirá el modal de análisis

2. **Configurar búsqueda:**
   - **Consulta:** Términos de búsqueda (ej: "factura", "invoice")
   - **Límite:** Número máximo de emails a analizar
   - Haz clic en "Analizar Emails"

3. **Revisar resultados:**
   - El sistema mostrará:
     - **Facturas encontradas:** Emails que contienen facturas
     - **Facturas con usuario:** Facturas que se pueden asignar automáticamente
     - **Facturas sin usuario:** Facturas que requieren asignación manual
     - **Ya procesadas:** Facturas que ya están en el sistema

4. **Seleccionar facturas:**
   - Marca las facturas que deseas procesar
   - Puedes seleccionar múltiples facturas
   - Revisa los datos extraídos de cada factura

5. **Procesar en lote:**
   - Haz clic en "Procesar Facturas Seleccionadas"
   - El sistema creará todas las facturas seleccionadas
   - Verás un resumen del procesamiento

### Gestión de Facturas sin Usuario

- **Facturas sin usuario:** Se marcan como "sin usuario" y pueden ser asignadas posteriormente
- **Asignación posterior:** Puedes editar estas facturas para asignar un usuario
- **Filtrado:** Usa el filtro de usuario para encontrar facturas sin asignar

## 👥 Gestión de Usuarios (Solo Administradores)

### Crear Usuario

1. **Acceder a usuarios:**
   - Ve a "Usuarios" en el menú principal
   - Haz clic en "Nuevo Usuario"

2. **Completar información:**
   - **Nombre:** Nombre completo del usuario
   - **Email:** Dirección de correo electrónico
   - **Rol:** Administrador o Colaborador

3. **Guardar:**
   - Haz clic en "Crear Usuario"
   - El usuario recibirá las credenciales por email

### Editar Usuario

1. **Acceder a edición:**
   - En la lista de usuarios, haz clic en el ícono de editar
   - Modifica los datos necesarios
   - Haz clic en "Actualizar Usuario"

## 📱 Uso en Móviles

### Navegación Móvil
- **Menú hamburguesa:** Toca el ícono ☰ para abrir/cerrar el menú
- **Vista de tarjetas:** Las facturas se muestran como tarjetas en móvil
- **Gestos táctiles:** Desliza para navegar entre páginas

### Optimizaciones Móviles
- **Botones grandes:** Optimizados para dedos
- **Campos de entrada:** Tamaño adecuado para teclado móvil
- **Carga rápida:** Optimizado para conexiones móviles

## 🔍 Consejos y Mejores Prácticas

### Para Carga Manual
- **Calidad de imagen:** Usa imágenes claras y bien iluminadas
- **Formato PDF:** Los PDFs de texto dan mejores resultados que imágenes escaneadas
- **Revisión:** Siempre revisa los datos extraídos por OCR

### Para Gmail
- **Filtros de búsqueda:** Usa términos específicos como "factura", "invoice", nombre del proveedor
- **Límite de emails:** Comienza con 50-100 emails para pruebas
- **Revisión regular:** Revisa las facturas detectadas antes de procesar

### Para Gestión General
- **Estados:** Usa los estados para organizar tu flujo de trabajo
- **Filtros:** Aprovecha los filtros para encontrar facturas específicas
- **Backup:** El sistema hace backup automático, pero mantén copias importantes

## ❓ Solución de Problemas

### Problemas Comunes

**1. Error al subir archivo:**
- Verifica que el archivo sea PDF, JPG o PNG
- Asegúrate de que el archivo no esté corrupto
- Intenta con un archivo más pequeño

**2. OCR no funciona correctamente:**
- Usa una imagen de mejor calidad
- Asegúrate de que el texto esté claro y legible
- Intenta con un PDF de texto en lugar de imagen

**3. Gmail no se conecta:**
- Verifica tu conexión a internet
- Asegúrate de que tu cuenta de Gmail esté activa
- Revisa que hayas autorizado el acceso correctamente

**4. Datos incorrectos en facturas:**
- Edita la factura manualmente
- Corrige los campos incorrectos
- Guarda los cambios

### Contacto de Soporte

Si encuentras problemas que no puedes resolver:
1. Revisa esta guía primero
2. Verifica la conexión a internet
3. Intenta recargar la página
4. Contacta al administrador del sistema

## 📈 Métricas y Reportes

### Dashboard
- **Estadísticas en tiempo real:** Ve el estado actual del sistema
- **Tendencias:** Analiza patrones en tus facturas
- **Métricas de Gmail:** Monitorea el procesamiento automático

### Exportación (Próximamente)
- **Reportes Excel:** Exporta datos para análisis externo
- **Reportes PDF:** Genera reportes formateados
- **Filtros avanzados:** Crea reportes personalizados

---

**Versión de la guía:** 1.0  
**Última actualización:** 5 de octubre de 2025  
**Sistema:** Gestión de Facturas v2.0
