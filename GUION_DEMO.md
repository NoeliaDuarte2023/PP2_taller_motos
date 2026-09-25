# Guion de demostración final — Grupo 10

**Sistema Web de Gestión para Taller de Motos** — Feature: Registro de clientes
**Duración total: 6 a 7 minutos**

---

## 0:00 – 0:40 | Problema y usuario

"Nuestro proyecto es un Sistema Web de Gestión para un Taller de Motos. El usuario principal es el personal del taller —recepción o dueño— que hoy registra a los clientes en papel. Nuestra primera funcionalidad digitaliza ese registro."

---

## 0:40 – 1:10 | Versión y alcance

"Lo que van a ver hoy es la feature 'Registro de clientes', validada y probada a lo largo de las últimas actividades (TP7 a TP11). No incluye todavía la gestión de motos, mecánicos ni repuestos — eso queda para una próxima etapa del PMF."

*(Mostrar brevemente el repositorio en GitHub: rama `main`, README.)*

---

## 1:10 – 4:30 | Flujo funcional principal

**Recorrido con datos preparados de antemano:**

1. Abrir `http://127.0.0.1:5000/` en el navegador — mostrar el formulario vacío.
2. Completar un cliente **válido y nuevo** (datos preparados, no sensibles).
3. Hacer clic en "Registrar cliente" → mostrar el cartel verde con el mensaje de éxito y el ID generado.
4. Abrir phpMyAdmin en otra pestaña (ya preparada) → tabla `clientes` → mostrar el registro recién insertado, con el mismo ID.

"Esto demuestra el circuito completo: formulario → backend Flask → validación → base de datos → confirmación al usuario."

---

## 4:30 – 5:30 | Validación / evidencia (caso alternativo)

**Elegir UNO de estos dos, según tiempo disponible:**

- **Opción A — Duplicado:** volver a cargar el mismo nombre y apellido del cliente recién registrado → mostrar el cartel rojo: *"Ya existe un cliente registrado con ese nombre y apellido"* (HTTP 409).
- **Opción B — Campo faltante:** dejar la dirección vacía y enviar → mostrar el cartel rojo indicando el campo faltante (HTTP 400).

"El backend valida de forma independiente del formulario — aunque alguien intente saltarse una validación visual, Flask la vuelve a controlar del lado del servidor."

---

## 5:30 – 6:20 | Decisiones técnicas

"Algunas decisiones que tomamos durante el desarrollo:"

- **Arquitectura:** Flask + MySQL, con el frontend como HTML simple que se comunica por `fetch` a la ruta `POST /clientes`.
- **Base de datos:** una sola tabla `clientes` por ahora, pensada para relacionarse más adelante con `motos` y `servicios`.
- **Seguridad:** las credenciales de conexión no están escritas en el código — se leen desde un archivo `.env` que no se sube al repositorio, y agregamos manejo de errores para que, si falla la base de datos, el usuario solo vea un mensaje genérico (nunca el detalle técnico interno de MySQL).
- **IA:** usamos IA como asistente en cada etapa —generación inicial del código, corrección de errores de seguridad, integración del formulario— pero cada sugerencia fue revisada, probada y en un caso (el de limpiar el formulario automáticamente) directamente revertida porque generó un comportamiento inestable. Esa decisión también quedó documentada.

---

## 6:20 – 7:00 | Cierre

"En resumen: la feature de registro de clientes está implementada y validada con evidencia real —cinco escenarios probados sin regresiones—. Queda una incidencia menor abierta y documentada (el formulario no se limpia solo después de un registro exitoso), que no bloquea el uso del sistema. El código está disponible públicamente en GitHub, con su documentación técnica completa en el README."

---

## Plan de contingencia

- Si XAMPP o Flask no arrancan durante la demo: tener listas las capturas de pantalla de TP10/TP11 (formulario con éxito, con error, y phpMyAdmin) para mostrar en su lugar.
- No modificar código durante la presentación — cualquier ajuste necesario se prueba después, fuera de la demo.
- Datos de prueba: usar nombres ficticios, no datos personales reales.

## Antes de empezar (checklist)

- [ ] XAMPP: Apache y MySQL en verde.
- [ ] Terminal con `python app_pp2.py` corriendo, sin errores.
- [ ] Pestaña del formulario (`http://127.0.0.1:5000/`) ya abierta.
- [ ] Pestaña de phpMyAdmin ya abierta, en la tabla `clientes`.
- [ ] Definido quién opera el teclado y quién explica.
- [ ] Capturas de respaldo a mano, por si falla el entorno en vivo.
