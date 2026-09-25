# Sistema Web de Gestión para Taller de Motos

**Grupo 10** · Prácticas Profesionalizantes II · Ciclo 2026

Sistema web para digitalizar el registro de clientes de un taller de motos, reemplazando el registro en papel. Esta primera versión implementa la feature prioritaria del PMF: **Registro de clientes**.

---

## Usuario principal

**Personal del taller** (recepción / dueño), quien carga los datos del cliente en el sistema durante la atención. (Esta definición se resolvió formalmente durante el TP11, unificando una ambigüedad detectada previamente entre "el cliente" y "el personal del taller".)

---

## Funcionalidades

| Estado | Funcionalidad |
|---|---|
| ✅ Implementado y validado | Registro de un cliente desde un formulario web (nombre, apellido, teléfono, dirección) |
| ✅ Implementado y validado | Validación en el backend de campos obligatorios, formato numérico del teléfono y prevención de duplicados (mismo nombre y apellido) |
| ✅ Implementado y validado | Persistencia del registro en MySQL, con respuesta de confirmación e ID generado |
| ✅ Implementado y validado | Manejo seguro de errores: ante una falla de conexión o inserción, el usuario recibe un mensaje genérico y el detalle técnico queda solo en el log del servidor |
| ✅ Implementado y validado | Configuración de la base de datos mediante variables de entorno (`.env`, excluido del repositorio) |
| ⚠️ Implementado con observaciones | El formulario no limpia sus campos automáticamente tras un registro exitoso — ver [Incidencias conocidas](#incidencias-conocidas) (INC-1) |
| ⏳ Pendiente | Validaciones visuales por campo en el formulario (mensajes de error puntuales, no solo un cartel general) |
| ⏳ Pendiente | Gestión de motos, mecánicos, repuestos y órdenes de trabajo (fuera del alcance de esta etapa) |

---

## Tecnologías

- **Backend:** Python 3 + Flask
- **Base de datos:** MySQL / MariaDB (vía XAMPP)
- **Frontend:** HTML + CSS + JavaScript (Fetch API, sin frameworks)
- **Configuración:** python-dotenv (variables de entorno)
- **Conector de base de datos:** mysql-connector-python
- **Control de versiones:** Git / GitHub

---

## Arquitectura y flujo de datos

```
Personal del taller
      │
      ▼
formulario.html  (GET /)
      │  fetch() → POST /clientes
      ▼
app_pp2.py — Flask
      │  valida campos, teléfono, duplicados
      ▼
mysql-connector-python
      │
      ▼
MySQL — base "pp2_taller_motos" — tabla "clientes"
      │
      ▼
Respuesta JSON (éxito con ID, o error) → formulario.html → mensaje en pantalla
```

**Responsabilidad de cada componente:**
- `templates/formulario.html`: interfaz de carga, arma la solicitud y muestra el resultado.
- `app_pp2.py` → ruta `GET /`: sirve el formulario.
- `app_pp2.py` → ruta `POST /clientes`: valida los datos recibidos, verifica duplicados, inserta el registro y responde.
- `.env`: credenciales de conexión a MySQL (no se versiona).
- Base de datos `pp2_taller_motos`, tabla `clientes`: almacenamiento persistente.

---

## Modelo de datos

**Base de datos:** `pp2_taller_motos`

### Tabla `clientes`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `nombre` | VARCHAR(100) | NOT NULL |
| `apellido` | VARCHAR(100) | NOT NULL |
| `telefono` | VARCHAR(20) | NOT NULL, validado como numérico en el backend |
| `direccion` | VARCHAR(200) | NOT NULL |

No se permiten dos registros con el mismo `nombre` + `apellido` (validado a nivel de aplicación, en la ruta `POST /clientes`).

---

## Requisitos previos

- [XAMPP](https://www.apachefriends.org/) (Apache + MySQL)
- [Python 3](https://www.python.org/) instalado y agregado al PATH
- Git (opcional, para clonar el repositorio)

---

## Instalación y puesta en marcha

1. **Cloná o descargá este repositorio.**
   ```
   git clone https://github.com/NoeliaDuarte2023/PP2_taller_motos.git
   cd PP2_taller_motos
   ```

2. **Instalá las dependencias de Python:**
   ```
   pip install -r requirements_pp2.txt
   ```

3. **Iniciá Apache y MySQL desde el panel de control de XAMPP.**

4. **Creá la base de datos y la tabla.** En phpMyAdmin (`http://localhost/phpmyadmin`), pestaña SQL:
   ```sql
   CREATE DATABASE IF NOT EXISTS pp2_taller_motos
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
   ```
   Entrá a la base recién creada y ejecutá:
   ```sql
   CREATE TABLE clientes (
       id INT AUTO_INCREMENT PRIMARY KEY,
       nombre VARCHAR(100) NOT NULL,
       apellido VARCHAR(100) NOT NULL,
       telefono VARCHAR(20) NOT NULL,
       direccion VARCHAR(200) NOT NULL
   ) ENGINE=InnoDB;
   ```

5. **Configurá las variables de entorno.** Copiá `.env.example` a un archivo nuevo llamado `.env` y completá los valores según tu instalación local (ver [Configuración](#configuración)).

6. **Iniciá el servidor:**
   ```
   python app_pp2.py
   ```

7. **Abrí el navegador en:** `http://127.0.0.1:5000/`

---

## Configuración

Las credenciales de conexión a la base de datos se leen desde un archivo `.env` (no incluido en el repositorio por seguridad). Se provee un archivo `.env.example` con las variables necesarias:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=pp2_taller_motos
```

Completá `.env` con los valores reales de tu entorno local de XAMPP antes de ejecutar el proyecto.

---

## Uso básico

1. Abrí `http://127.0.0.1:5000/` en el navegador.
2. Completá Nombre, Apellido, Teléfono y Dirección.
3. Hacé clic en **Registrar cliente**.
4. El sistema muestra un mensaje de éxito (con el ID generado) o un mensaje de error indicando qué corregir.

---

## Estructura del proyecto

```
PP2_taller_motos/
├── app_pp2.py              # Backend Flask: rutas GET / y POST /clientes
├── templates/
│   └── formulario.html     # Frontend: formulario de registro
├── requirements_pp2.txt    # Dependencias de Python
├── .env.example            # Plantilla de variables de entorno (sin datos reales)
├── .env                    # Variables de entorno reales (NO versionado)
└── .gitignore               # Excluye .env del control de versiones
```

---

## Pruebas y estado

Durante el TP11 se ejecutaron 5 casos funcionales, todos desde el formulario real (navegador), con evidencia de las respuestas HTTP y de la persistencia en la base de datos:

| Caso | Escenario | Resultado esperado | Estado |
|---|---|---|---|
| PF-1 | Registro válido | HTTP 201 + ID generado + registro en MySQL | ✅ Cumple |
| PF-2 | Campo obligatorio faltante | HTTP 400 con el campo indicado | ✅ Cumple |
| PF-3 | Teléfono con formato inválido | HTTP 400 | ✅ Cumple |
| PF-4 | Cliente duplicado (mismo nombre y apellido) | HTTP 409 | ✅ Cumple |
| PF-5 | Falla controlada de conexión a MySQL | HTTP 500 con mensaje genérico; detalle técnico solo en el log del servidor | ✅ Cumple |

No se detectaron regresiones tras las correcciones aplicadas en TP9 (variables de entorno, ocultamiento de errores internos).

---

## Incidencias conocidas

| ID | Descripción | Severidad | Prioridad | Estado |
|---|---|---|---|---|
| INC-1 | El formulario no limpia sus campos automáticamente tras un registro exitoso; el usuario debe borrarlos a mano antes de cargar un nuevo cliente. | Baja | Baja | Abierta (se intentó una corrección durante TP11, provocó un comportamiento inestable en el entorno de pruebas y se revirtió; queda pendiente para una futura iteración). No bloquea el uso del sistema. |

---

## Uso de IA durante el desarrollo

El proyecto se construyó con asistencia de IA en distintas etapas, siempre con revisión y decisión final del equipo:

- **TP7–TP8:** generación inicial de la ruta `POST /clientes` a partir de un prompt técnico estructurado (rol, contexto, criterios de aceptación, restricciones). El equipo detectó y corrigió credenciales de conexión inventadas por la IA.
- **TP9:** se usó IA para proponer el traslado de credenciales a variables de entorno (`.env` + `python-dotenv`) y para ocultar del cliente los detalles internos de errores de MySQL. Ambas correcciones se probaron y confirmaron sin regresiones.
- **TP10:** se usó IA para construir el formulario HTML de integración y la ruta `GET /` que lo sirve, sin modificar la lógica ya validada de `POST /clientes`.
- **TP11:** se usó IA para proponer una corrección de la incidencia INC-1 (limpiar el formulario tras el éxito). La corrección provocó un problema no resuelto en el entorno de pruebas del equipo y fue revertida; la incidencia quedó documentada como pendiente.

En todos los casos, el equipo revisó críticamente el código generado, lo probó con datos reales y decidió qué aceptar, ajustar o descartar antes de integrarlo.

---

## Equipo

**Grupo 10**
- Duarte, Noelia Itatí
- Hauff, Ezequiel
- Fleitas, Liliana

---

## Evidencias y demo

Las capturas de pantalla de las pruebas funcionales (TP11) y de la integración (TP10) se encuentran en la carpeta de entregas del grupo. El recorrido de demostración se detalla en `GUION_DEMO.md`.

**Repositorio:** https://github.com/NoeliaDuarte2023/PP2_taller_motos
