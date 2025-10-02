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

### Fase 2 – OCR + Gmail (en desarrollo)  
- Integración Gmail API.  
- OCR para facturas físicas.  
- Dashboard web avanzado.  

### Fase 2.5 – Conciliación y Control (nueva 🚀)  
- Módulo de conciliación automática con extractos.  
- Campos de método de pago detallados.  
- Alertas de cumplimiento (antes del día 5).  
- Almacenamiento en nube.  
- Reporte contable final con códigos para Siigo.  

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
