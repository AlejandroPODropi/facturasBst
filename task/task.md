# 🗂 TASK.md – Proyecto Control de Facturas Boosting  

## 📌 Fase 1 – MVP ✅ (Completada)  
- Configuración proyecto base  
- Modelado DB (users, invoices)  
- Endpoints CRUD facturas  
- Exportación a Excel  
- Validación facturas  
- Frontend inicial (dashboard, formulario, usuarios)  
- Filtros avanzados  
- Visualizador de archivos  
- Dashboard con estadísticas  
- Pruebas unitarias  

---

## 📌 Fase 2 – OCR + Gmail (En desarrollo)  
- ✅ Integración Gmail API (backend + frontend)  
- ✅ OCR para facturas físicas (backend + frontend)  
- Dashboard avanzado con métricas en tiempo real  
- Interfaz de validación con edición de datos extraídos  
- Patrones OCR optimizados  

---

## 📌 Fase 2.5 – Conciliación y Control (Nuevo 🚀)  
1. **Conciliación automática**  
   - Carga de extractos CSV/Excel  
   - Comparación movimientos vs facturas  
   - Reporte con estados (con factura, sin factura, factura sin movimiento)  

2. **Método de pago detallado**  
   - Campos: `TARJETA_BST`, `TARJETA_PERSONAL`, `EFECTIVO`  
   - Filtros por método de pago  

3. **Almacenamiento en nube**  
   - Integración OneDrive/GCP Storage  
   - Organización por colaborador/mes  

4. **Alertas de cumplimiento**  
   - Notificaciones automáticas a día 3  
   - Dashboard con % cumplimiento  

5. **Reporte contable final**  
   - Exportación Excel/CSV con NIT, Razón Social, Concepto, Código contable, Valor, IVA, Método de pago  
   - Movimientos sin soporte → marcados “descuento nómina”  

---

## 📌 Fase 3 – Escalamiento  
- Clasificación de gastos con IA  
- Integración directa con Siigo  
- Optimización de pagos  

---

## 📌 Responsive – Checklist (Transversal Fase 2)  
- [ ] Sidebar colapsa en móvil  
- [ ] Formulario carga factura mobile-first  
- [ ] Tablas → vista dual  
- [ ] Dashboard con grid adaptativo  
- [ ] Testing Chrome DevTools + Lighthouse  
- [ ] Validación accesibilidad (WCAG 2.1)  
