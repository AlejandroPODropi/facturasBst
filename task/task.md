# 🗂 TASK.md – Proyecto Control de Facturas Boosting

## 📌 Tareas Completadas (Fase 1 – MVP) ✅

1. **Configurar proyecto base** ✅

   * ✅ Crear estructura inicial del repo (`src/`, `tests/`, `tasks/`, `.env.example`, `README.md`).
   * ✅ Configurar entorno con FastAPI y PostgreSQL.
   * ✅ Crear archivo `requirements.txt`.

2. **Diseñar modelo de datos** ✅

   * ✅ Tabla `users` (id, nombre, correo, rol).
   * ✅ Tabla `invoices` (id, user_id, fecha, proveedor, monto, método_pago, categoría, archivo, estado).
   * ✅ Definir migraciones iniciales con SQLAlchemy.

3. **Endpoint de carga de facturas** ✅

   * ✅ POST `/invoices/upload` para registrar factura manual.
   * ✅ Validaciones: archivo adjunto, monto > 0, categoría requerida.
   * ✅ Guardar referencia en DB y archivo en almacenamiento local (Fase 1).

4. **Endpoint de consulta de facturas** ✅

   * ✅ GET `/invoices` con filtros por usuario, fecha, estado.
   * ✅ Paginación básica.

5. **Exportación a Excel** ✅

   * ✅ Endpoint GET `/invoices/export` → genera archivo Excel con facturas por usuario/mes.
   * ✅ Incluir campos: id, colaborador, proveedor, monto, método de pago, estado.

6. **Sistema de validación de facturas** ✅

   * ✅ Endpoint PATCH `/invoices/{id}/validate` para validar/rechazar facturas.
   * ✅ Cambio de estado: pendiente → validada/rechazada.
   * ✅ Notas de validación opcionales.

7. **Frontend completo** ✅

   * ✅ Dashboard con estadísticas básicas.
   * ✅ Página de usuarios (listar).
   * ✅ Página de facturas (listar con filtros).
   * ✅ Formulario de creación de facturas.
   * ✅ Modal de validación de facturas.
   * ✅ Navegación responsive.

8. **Pruebas unitarias completas** ✅

   * ✅ Caso éxito: subir factura válida.
   * ✅ Caso borde: monto = 0.
   * ✅ Caso fallo: archivo inválido o sin categoría.
   * ✅ Tests de validación de facturas.

9. **Gestión completa de usuarios** ✅

   * ✅ CRUD completo de usuarios en el frontend.
   * ✅ Formularios de creación y edición de usuarios.
   * ✅ Modal de confirmación de eliminación.
   * ✅ Validaciones en tiempo real.

10. **Filtros avanzados** ✅

   * ✅ Mejorar filtros en la página de facturas.
   * ✅ Búsqueda por texto en proveedor y descripción.
   * ✅ Filtros por rango de fechas.
   * ✅ Filtros por usuario, estado, categoría y método de pago.
   * ✅ Componente de filtros expandible con limpieza de filtros.

11. **Visualizador de archivos en modal de validación** ✅

   * ✅ Endpoint para servir archivos adjuntos.
   * ✅ Validación de permisos y existencia de archivos.
   * ✅ Soporte para múltiples tipos de archivo (PDF, imágenes, Excel).
   * ✅ Visualizador integrado en modal de validación.
   * ✅ Vista previa de PDFs e imágenes.
   * ✅ Botón de apertura para archivos no visualizables.
   * ✅ Información completa de la factura en el modal.
   * ✅ Manejo de errores y validaciones.

12. **Dashboard avanzado con estadísticas en tiempo real** ✅

   * ✅ Servicio de estadísticas del dashboard.
   * ✅ Endpoint completo con múltiples métricas.
   * ✅ Gráficos interactivos (barras, líneas, pie charts).
   * ✅ Estadísticas por usuario con ranking.
   * ✅ Tendencias mensuales con insights.
   * ✅ Distribución por categorías y métodos de pago.
   * ✅ Métricas de rendimiento de validación.
   * ✅ Componentes React reutilizables.
   * ✅ Tests unitarios completos.
   * ✅ Dashboard principal con datos en tiempo real.

## 📌 Tareas Pendientes (Fase 1 – MVP)

**¡MVP Fase 1 COMPLETADO AL 100%! 🎉**

---

## 📌 Backlog (próximas fases)

* **Integración correo electrónico:** recepción automática de facturas electrónicas desde Gmail/Outlook.
* **OCR:** extracción de datos de facturas físicas (PDF/JPG).
* **Dashboard web:** para visualizar facturas pendientes, aprobadas, rechazadas.
* **Clasificación automática:** categorización de gastos con IA.
* **Integración contable:** conexión con software de contabilidad.
* **Optimización pagos:** centralización de métodos de pago de empleados.

---

## 📌 Tareas Descubiertas (se irán sumando)

* Definir storage definitivo (Google Cloud Storage, S3, etc.).
* Crear roles de usuario (colaborador, auxiliar contable, administrador).
* Autenticación (JWT o similar).


