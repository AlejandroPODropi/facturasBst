FRONTEND_RESPONSIVE_PLAN.md

Proyecto: Control de Facturas – Boosting

🎯 Objetivo

Asegurar que la aplicación sea totalmente responsive, priorizando el uso en dispositivos móviles (colaboradores en campo) sin sacrificar la experiencia en escritorio (auxiliar contable y gerencia).

📌 Alcance

Adaptar layout, formularios, tablas y dashboards a distintos tamaños de pantalla.

Garantizar que la experiencia de usuario sea fluida tanto en móvil, tablet y desktop.

Incluir pruebas de usabilidad y accesibilidad.

🔄 Fases del Plan Responsive
1. Layout principal con Sidebar

Sidebar colapsable automáticamente en pantallas pequeñas.

Navbar simplificado en móviles.

Breakpoints recomendados:

sm: <640px (móvil)

md: 641-1024px (tablet)

lg: >1024px (desktop)

2. Formularios adaptativos (mobile-first)

Formulario de carga de factura debe funcionar con 2 pasos máximo en móvil.

Inputs y botones con tamaño adecuado para dedos (mín. 44px de alto).

Validaciones visibles y claras (ej. campo obligatorio resaltado).

3. Tablas con vista dual

Desktop: tabla tradicional con columnas (facturas, fechas, montos, estados).

Móvil: vista en cards → cada factura en tarjeta con campos clave (razón social, monto, estado, botón “ver detalle”).

Scroll horizontal habilitado solo si es estrictamente necesario.

4. Dashboard con Grid Responsive

Desktop: hasta 4 tarjetas en fila.

Tablet: 2 tarjetas en fila.

Móvil: 1 tarjeta por fila.

Gráficas con librerías que soporten redimensionamiento automático (ej. Recharts, Chart.js).

5. Testing y Optimización

Testing responsive:

Chrome DevTools: simular pantallas (iPhone, Galaxy, iPad, Desktop).

Pruebas manuales en dispositivos reales (mín. 2 móviles distintos).

Testing accesibilidad:

Labels descriptivos en todos los inputs.

Contraste mínimo AA (WCAG 2.1).

Navegación por teclado y compatibilidad con lectores de pantalla.

Optimización:

Lazy loading de imágenes de facturas.

Minificación de assets.

Evaluación de performance con Lighthouse (>80 en móvil).

🛠️ Frameworks y Herramientas recomendadas

TailwindCSS: utilidades responsivas (sm:, md:, lg:).

React + Hooks: manejo de estado para vista dual.

Framer Motion: transiciones fluidas en mobile.

Jest/Playwright: pruebas de UI automatizadas.

✅ Checklist de verificación responsive
Layout

 Sidebar colapsa en móvil

 Navbar simplificado en móvil

 Breakpoints aplicados

Formularios

 Inputs legibles en móvil

 Botones accesibles (>44px)

 Validaciones visibles

Tablas

 Vista tabla en desktop

 Vista cards en móvil

 Scroll controlado

Dashboard

 Grid 4/2/1 tarjetas según tamaño

 Gráficas redimensionables

 Textos legibles

Testing

 Chrome DevTools en distintos dispositivos

 Lighthouse >80 en móvil

 Prueba accesibilidad básica (teclado + contraste)

📌 Nota: Tras implementar cada fase, actualizar FRONTEND_DEPLOYMENT_COMPLETE.md con evidencia (capturas de pantalla y métricas de pruebas).


🗂 TASK.md – Sección Responsive (Fase 2)
📌 Tareas Activas – Responsive

Layout principal con Sidebar

Implementar sidebar colapsable en móviles.

Navbar simplificado para pantallas <640px.

Aplicar breakpoints (sm, md, lg).

Formularios adaptativos (mobile-first)

Optimizar formulario de carga de factura para uso móvil.

Asegurar inputs y botones ≥44px de alto.

Validaciones visibles y adaptadas a pantallas pequeñas.

Tablas con vista dual

En desktop: vista tabla tradicional.

En móvil: vista en cards con campos clave.

Controlar scroll horizontal solo si es necesario.

Dashboard responsive con Grid

Desktop: hasta 4 tarjetas por fila.

Tablet: 2 tarjetas por fila.

Móvil: 1 tarjeta por fila.

Gráficas redimensionables automáticamente.

Testing y Optimización

Probar en Chrome DevTools (iPhone, Galaxy, iPad, Desktop).

Verificar en mínimo 2 dispositivos reales.

Lighthouse >80 en móvil.

Validar accesibilidad (contraste, navegación teclado, labels).

Implementar lazy loading de imágenes y minificación de assets.

📌 Backlog – Responsive

Agregar dark mode opcional.

Mejorar transiciones con Framer Motion.

Automatizar pruebas de UI con Playwright/Jest.

