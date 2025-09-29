Proyecto Control de Facturas Boosting

## 1. Propósito del Proyecto

Desarrollar un sistema digital para el **registro, validación y consolidación de facturas** de los colaboradores de Boosting.
El objetivo es reducir errores operativos, optimizar la carga del área contable y asegurar que todos los gastos queden soportados para su correcta deducción tributaria.

---

## 2. Alcance

* Captura de facturas electrónicas (vía correo) y físicas (fotos/PDF).
* Registro por colaborador con clasificación de gasto y método de pago.
* Consolidación automática de facturas por empleado y por mes.
* Reportes exportables en Excel/CSV.
* Dashboard para auxiliar contable con facturas pendientes, validadas y rechazadas.

---

## 3. Usuarios finales

* **Colaboradores en campo:** registran facturas desde móvil/web.
* **Auxiliar contable:** valida, consolida y exporta la información.
* **Gerencia financiera:** accede a reportes globales para toma de decisiones.

---

## 4. Arquitectura inicial

* **Backend:** FastAPI (Python).
* **Frontend:** React (web) + posible app móvil (Flutter o React Native en fase 2).
* **Base de datos:** PostgreSQL.
* **Integraciones:**

  * Gmail/Outlook API para recepción de facturas electrónicas.
  * OCR (Tesseract u otro servicio) para facturas físicas.
* **Infraestructura:** despliegue en Google Cloud (Docker).

---

## 5. Fases del proyecto

### **Fase 1 (MVP – 1 mes)**

* Registro manual de facturas vía web/app.
* Consolidador en base de datos.
* Exportación a Excel.

### **Fase 2 (2-3 meses)**

* Integración con correo para facturas electrónicas.
* OCR para facturas físicas.
* Dashboard de control.

### **Fase 3 (4-6 meses)**

* Clasificación automática de gastos con IA.
* Integración con software contable.
* Optimización de métodos de pago.

---

## 6. Métricas y OKRs Globales

* Reducir en **≥90% los errores operativos** en la gestión de facturas.
* Garantizar que **100% de las facturas** queden registradas en el sistema.
* Disminuir en **≥50% la carga operativa** del auxiliar contable.
* Reducir los gastos no deducibles a **<5%** del total de facturas.
* Adopción del **100% de colaboradores** en campo en los primeros 6 meses.

---

## 7. Buenas prácticas

* Código modular, máximo 500 líneas por archivo.
* Docstrings en todas las funciones.
* Uso de type hints en Python.
* Pruebas unitarias (éxito, borde, fallo) para cada funcionalidad.
* Actualizar siempre `README.md` y `TASK.md` tras cada cambio.

---


