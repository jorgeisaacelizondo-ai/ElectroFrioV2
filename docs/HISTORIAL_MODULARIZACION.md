# 📋 HISTORIAL Y ESTADO DE MODULARIZACIÓN - ELECTROFRÍO V2
*Fecha de actualización: 28 de Octubre de 2026*

Este documento preserva todo el historial de decisiones técnicas, arquitectura, progreso de modularización y la verificación completa de todos los módulos del sistema.

---

## 🏗️ 1. Resumen Ejecutivo y Resultados

- **Líneas originales en `index.html`:** **16.011 líneas** (monolito).
- **Líneas actuales en `index.html`:** **1.364 líneas** (App Shell ultra-limpio).
- **Reducción total:** **14.647 líneas eliminadas del archivo principal (-91.5%)**.
- **Módulos totalmente independientes en `modulos/`:** **17 módulos HTML completos**.
- **Entorno de ejecución local:** `http://localhost:3000` (servidor `serve`).
- **Estado de endpoints:** **100% saludables (HTTP 200 OK en los 18 endpoints)**.
- **Errores de sintaxis JS:** **0 errores en todos los módulos y en `index.html`**.

---

## 🛡️ 2. Reglas Técnicas y Arquitectura del Sistema

1. **Arquitectura App Shell + Micro-Frontends / Módulos:**
   - `index.html` actúa exclusivamente como el contenedor maestro (App Shell): maneja la autenticación Firebase, la sesión en `localStorage`, la barra superior, la navegación lateral (sidebar) y el bus de mensajes.
   - Cada pantalla es una aplicación web independiente dentro del directorio `modulos/`, con su propio CSS, DOM y lógica.
2. **Modo Seguro Firestore (`js/modo-seguro.js`):**
   - Incluido en la cabecera de **todos** los módulos independientes (`../js/modo-seguro.js`) y en `index.html`.
   - Evita sobreescrituras accidentales en producción durante desarrollo local.
3. **Scroll Único (Cero Doble Scroll):**
   - Todos los iframes usan `calc(100vh - 72px)` en escritorio y `calc(100vh - 60px)` en móvil.
   - La clase `.iframe-active` en `#contentArea` previene desbordes y scrolls dobles.
4. **Carga Perezosa (Lazy Loading):**
   - Los módulos se cargan bajo demanda vía `<iframe data-src="modulos/nombre.html">`.
   - `switchTab(moduleName)` asigna `iframe.src = iframe.getAttribute('data-src')` únicamente al ser visitados por el usuario, maximizando la velocidad de inicio de la aplicación y ahorrando ancho de banda y batería en dispositivos móviles.
5. **Mobile First (≤ 768px):**
   - Menú lateral deslizable (drawer móvil) con backdrop táctil y auto-cierre al seleccionar opción.
   - Tablas responsivas transformadas en tarjetas táctiles en pantallas pequeñas.
6. **Event Bus Bidireccional (`postMessage`):**
   - Comunicación fluida entre iframes y el App Shell mediante `window.parent.postMessage({ type: '...' }, '*')`.
   - `NAVIGATE`: cambio de pestaña solicitado por un submódulo (ej. accesos rápidos del Dashboard).
   - `SHOW_TOAST`: notificación flotante global mostrada por el App Shell.
   - `FICHAJE_UPDATED`, `ORDER_UPDATED`, `COLLABORATOR_UPDATED`, `CLIENT_UPDATED`, `ORDER_COMPLETED`: retransmitidos en tiempo real por el App Shell a todos los iframes activos para mantener sincronía sin recargas completas.
7. **Optimización de Lecturas en Firestore:**
   - Lecturas iniciales de estado (fichajes, órdenes) cacheadas en `localStorage` con estrategia offline-first.
   - El mapa de técnicos y el dashboard redujeron su consumo en más de un 95% al no solicitar lotes innecesarios de fichajes pasados en cada apertura.

---

## 📦 3. Detalle de los 17 Módulos Modularizados

### 1. Dashboard Principal (`modulos/dashboard.html`)
- Vistas adaptadas automáticamente para Administrador y Colaborador.
- Lectura directa de `localStorage` para un tiempo de carga instantáneo (0 lecturas iniciales de Firestore).
- Tarjetas de métricas y KPIs en vivo (Órdenes Activas, Técnicos en Servicio, Fichajes de Hoy).
- Tabla de órdenes de trabajo recientes con badges de estado y accesos directos.
- Indicador de estado de jornada y cuenta regresiva de cooldown para colaboradores.
- Accesos directos con eventos `NAVIGATE` hacia otros módulos.

### 2. Colaboradores (`modulos/colaboradores.html`)
- Sincronización en tiempo real con la colección `usuarios` de Firestore.
- Creación de técnicos vía instancia secundaria de Firebase Auth para evitar desconectar al administrador activo.
- Configuración de base y geocerca GPS por colaborador.
- Detección de estado online/en servicio vía fichajes del día.
- Notificación cruzada `COLLABORATOR_UPDATED`.

### 3. Clientes (`modulos/clientes.html`)
- Directorio de clientes con autocompletado y búsqueda instantánea.
- Soporte para múltiples domicilios y coordenadas GPS por cliente.
- Enlace directo a Google Maps (`🗺️ Maps`) y WhatsApp (`💬`).
- Modal de nuevo/editar cliente centrado (`#modalNuevoClienteCentered`).
- Modal de historial de planillas y trabajos realizados por cliente (`#modalHistorialCliente`).
- Notificación cruzada `CLIENT_UPDATED`.

### 4. Mapa de Técnicos en Tiempo Real (`modulos/mapa.html`)
- **Optimización de Lecturas en Firestore:** Se eliminó la descarga de 350 fichajes de la nube. El estado en servicio se lee directamente desde `localStorage` (`0 lecturas en fichajes`), reduciendo el consumo total al abrir el mapa de ~350 lecturas a únicamente 5-10 lecturas (solo la colección de colaboradores).
- Integración limpia con Leaflet 1.9.4 y OpenStreetMap sin conflictos globales.
- Escucha en vivo de posiciones GPS de técnicos en servicio (`usuarios.where('role', '==', 'Colaborador')`).
- Marcadores personalizados con iniciales, colores únicos basados en hash y animación de pulso verde en vivo.
- Algoritmo de dispersión angular para prevenir superposición de pines a menos de 8 metros.
- Panel lateral deslizable (sidebar en escritorio, drawer en móvil) con lista interactiva de técnicos.
- Acciones de centrar en técnico (`focusTechnician`), centrar en todos (`centerMapOnAll`) y botón de navegación en Google Maps.
- Filtro interactivo por estado: *Todos*, *🟢 En Servicio*, *⚪ Fuera de Turno*.

### 5. Configuración y Resguardo (`modulos/configuracion.html`)
- Sistema con pestañas organizadas:
  1. **General y Precios:** Nombre de empresa, email, zona horaria y fórmula de precio sugerido PDT (Monto base + multiplicador variable) con previsualización en vivo.
  2. **Centro de Resguardo (Backups):** Descarga completa en JSON de 13 colecciones Firestore, estado y tiempo transcurrido desde el último backup, y modal de restauración de backup con previsualización de documentos e inserción en lotes (`batch.commit`).
  3. **Historial de Importaciones:** Auditoría en tiempo real de cargas masivas Excel/CSV con mapeo de campos.
  4. **Migración y Base de Datos:** Carga masiva de `datos/historial_parsed.json` a Cloud Firestore con barra de progreso en tiempo real.
- Parámetro URL `?tab=importaciones` que permite al botón de navegación "Importaciones" abrir directamente la pestaña correspondiente.

### 6. Órdenes de Trabajo (`modulos/ordenes.html`)
- Gestión integral de órdenes con filtros por estado, prioridad, técnico y fecha.
- Modales independientes para nueva orden, detalle de orden y órdenes no coordinadas.
- Integración fluida con `planillas.html` mediante `OPEN_PLANILLA_FOR_ORDER`.

### 7. Fichajes y Asistencia (`modulos/fichajes.html`)
- Registro de entrada, en servicio y salida con validación GPS y geocerca.
- Límite de carga a los últimos 5 días para optimizar lecturas en Firebase, con botón para cargar historial extendido bajo demanda.
- Visualización detallada de fichajes (botón del ojo 100% operativo).
- Modal autónomo de registro manual de fichajes para administradores.

### 8. Jornales (`modulos/jornales.html`)
- Liquidación automática por técnico, horas trabajadas y planillas asignadas.
- Exportación de recibos de jornales en PDF membretado.

### 9. Planillas de Trabajo - PDT (`modulos/planillas.html`)
- Formulario digital multi-área de refrigeración, electricidad, domótica, etc.
- 12 estados de trabajo con colores distintivos y estado de impresión.
- Generación de hojas técnicas de trabajo y exportación a Excel.

### 10. Tareas Pendientes (`modulos/tareas.html`)
- Tablero Kanban / lista de tareas por prioridad con filtros de colaborador y fecha.

### 11. Calendario de Servicios (`modulos/calendario.html`)
- Integración con FullCalendar 6 para visualización mensual, semanal y diaria de órdenes.

### 12. Materiales e Insumos (`modulos/materiales.html`)
- Catálogo de repuestos con control de inventario y costos.

### 13. Mano de Obra (`modulos/manodeobra.html`)
- Tarifario configurable de servicios y tareas especializadas.

### 14. Presupuestos (`modulos/presupuestos.html`)
- Cotizador digital de presupuestos para clientes con exportación PDF.

### 15. Proveedores (`modulos/proveedores.html`)
- Directorio de proveedores, rubros comerciales y contactos.

### 16. CRM Clientes y Prospectos (`modulos/crm.html`)
- Pipeline de oportunidades comerciales, seguimiento y etapas de conversión.

### 17. Cobros y Cuentas Corrientes (`modulos/cobros.html`)
- Control de saldos, cuentas corrientes de clientes, pagos y cobranzas.

---

## 🔍 4. Matriz de Pruebas y Salud del Sistema

| Endpoint | Código HTTP | Sintaxis JS | Estado |
| :--- | :---: | :---: | :---: |
| `/` (`index.html`) | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/dashboard` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/ordenes` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/tareas` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/calendario` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/fichajes` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/planillas` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/jornales` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/colaboradores` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/clientes` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/mapa` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/materiales` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/manodeobra` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/presupuestos` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/proveedores` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/crm` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/cobros` | 200 OK | 0 errores | ✅ Operativo |
| `/modulos/configuracion` | 200 OK | 0 errores | ✅ Operativo |
