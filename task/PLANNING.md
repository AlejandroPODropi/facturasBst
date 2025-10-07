# 📑 PLANNING.md – Proyecto Control de Facturas Boosting  

## 1. Propósito del Proyecto  
Desarrollar un sistema digital para el **registro, validación, conciliación y consolidación de facturas** de los colaboradores de Boosting.  
El objetivo es reducir errores operativos, optimizar la carga del área contable y asegurar que todos los gastos queden soportados para su correcta deducción tributaria.  

---

## 2. Alcance  
- Captura de facturas electrónicas (correo) y físicas (fotos/PDF).  
- Registro por colaborador con clasificación de gasto y método de pago detallado.  
- Consolidación automática por empleado y mes.  
- Reportes exportables en Excel/CSV para Siigo.  
- Dashboard para auxiliar contable con facturas pendientes, validadas y rechazadas.  
- Conciliación automática contra extractos bancarios.  
- Alertas y control de cumplimiento (fecha límite 5 de cada mes).  
- Plataforma totalmente responsive (mobile-first).  

---

## 3. Usuarios finales  
- **Colaboradores en campo:** suben facturas desde móvil/web.  
- **Auxiliar contable:** valida, consolida y descarga reportes.  
- **Gerencia financiera:** accede a reportes globales.  

---

## 4. Arquitectura  
- **Backend:** FastAPI (Python).  
- **Frontend:** React (web) con Tailwind (responsive).  
- **Base de datos:** PostgreSQL.  
- **Integraciones:**  
  - Gmail/Outlook API → facturas electrónicas.  
  - OCR (Tesseract u otros) → facturas físicas.  
  - OneDrive/GCP Storage → almacenamiento en nube.  
- **Infraestructura:** Google Cloud con Docker.  

---

## 5. Fases del Proyecto  

### Fase 1 – MVP (completada ✅)  
- Registro manual de facturas vía web/app.  
- Consolidación en base de datos.  
- Exportación a Excel.  
- Validación de facturas.  
- Frontend con dashboard inicial.  

### Fase 2 – OCR + Gmail (completada ✅)  
- ✅ Integración Gmail API.  
- ✅ OCR para facturas físicas.  
- ✅ Dashboard web avanzado.  

### Fase 2.5 – Conciliación y Control (completada ✅)  
- ✅ Módulo de conciliación automática con extractos.  
- ✅ Campos de método de pago detallados.  
- ✅ Alertas de cumplimiento (antes del día 5).  
- ✅ Almacenamiento en nube.  
- ✅ Reporte contable final con códigos para Siigo.

### Fase 2.6 – Resolución de Problemas (completada ✅)  
- ✅ Corrección de conflictos de rutas en FastAPI
- ✅ Manejo robusto de datos nulos en frontend
- ✅ Validación de esquemas Pydantic
- ✅ Optimización de gráficos SVG
- ✅ Despliegue y documentación completa

### Fase 2.7 – Correcciones de Métodos de Pago y Archivos Adjuntos (completada ✅)  
- ✅ Corrección de valores de métodos de pago (mayúsculas vs minúsculas)
- ✅ Implementación de enlaces de descarga para archivos adjuntos de Gmail
- ✅ Mejora de extracción de montos en facturas colombianas
- ✅ Eliminación de usuario "Sin Usuario" no deseado
- ✅ Corrección de dropdown de usuarios en edición de facturas
- ✅ Despliegue completo de correcciones

### Fase 2.8 – Resolución de Problemas de Base de Datos y CORS (completada ✅)
- ✅ Corrección de conexión a base de datos con credenciales correctas
- ✅ Habilitación de Secret Manager API en Google Cloud
- ✅ Migración exitosa de credenciales Gmail a Secret Manager
- ✅ Corrección de etiquetas de Secret Manager para cumplir con regex
- ✅ Resolución de errores 500 en endpoints del backend
- ✅ Verificación de funcionamiento de todos los endpoints críticos
- ✅ Estabilización completa del sistema en producción  

### Fase 3 – Escalamiento (4-6 meses)  
- Clasificación automática de gastos con IA.  
- Integración con Siigo u otro software contable.  
- Optimización de métodos de pago.  

---

## 6. Plan Responsive  
- **Mobile-first** → prioridad en formulario de carga.  
- **Sidebar colapsable** y navbar simplificado.  
- **Formularios adaptativos** (inputs accesibles, validaciones visibles).  
- **Tablas duales** → tabla en desktop, tarjetas en móvil.  
- **Dashboard responsive** con grids adaptativos.  
- **Testing y accesibilidad** (Chrome DevTools, Lighthouse >80, WCAG 2.1).  

---

## 7. OKRs Globales  
- Reducir en ≥90% los errores operativos en gestión de facturas.  
- Garantizar que 100% de facturas estén registradas antes del cierre.  
- Reducir en ≥50% la carga del auxiliar contable.  
- Reducir gastos no deducibles a <5%.  
- Adopción del 100% de colaboradores en 6 meses.  
