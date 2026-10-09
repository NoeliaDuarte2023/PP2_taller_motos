# Librerias necesarias
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
from werkzeug.security import check_password_hash
import mysql.connector
import os
import re
from datetime import date, datetime
from decimal import Decimal
from dotenv import load_dotenv

# Cargar las variables definidas en el archivo .env
load_dotenv()

app = Flask(__name__)

# Clave secreta para firmar la sesion; se lee desde el archivo .env
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Falta SECRET_KEY en el archivo .env")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Funcion para obtener la conexion a la base de datos MySQL
# Las credenciales se leen desde variables de entorno (archivo .env)
def obtener_conexion():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Decorador: exige haber iniciado sesion para usar una ruta
def login_requerido(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            # Los pedidos del formulario (POST) reciben JSON; el navegador es enviado al login
            if request.method == "POST":
                return jsonify({"error": "Debe iniciar sesion para continuar."}), 401
            return redirect(url_for("login"))
        return funcion(*args, **kwargs)
    return envoltura

# Ruta que sirve el formulario de registro de clientes (frontend)
@app.route("/", methods=["GET"])
@login_requerido
def formulario_clientes():
    return render_template("formulario.html")

@app.route("/clientes", methods=["POST"])
@login_requerido
def registrar_cliente():
    # 1) Recibir los datos enviados desde el formulario
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()

    # 2) Validar que ningun campo obligatorio este vacio
    campos_faltantes = []
    if not nombre:
        campos_faltantes.append("nombre")
    if not apellido:
        campos_faltantes.append("apellido")
    if not telefono:
        campos_faltantes.append("telefono")
    if not direccion:
        campos_faltantes.append("direccion")

    if campos_faltantes:
        return jsonify({
            "error": "Faltan campos obligatorios.",
            "campos_faltantes": campos_faltantes
        }), 400

    # 3) Validar que el telefono tenga formato numerico valido
    if not telefono.isdigit():
        return jsonify({"error": "El telefono debe contener solo numeros."}), 400

    # Manejo de error si falla la conexion a MySQL (por ejemplo, servidor caido)
    try:
        conexion = obtener_conexion()
    except mysql.connector.Error as error:
        # El detalle tecnico completo queda solo en el log del servidor,
        # nunca se lo mostramos al usuario final
        print(f"[ERROR INTERNO] Fallo de conexion a MySQL: {error}")
        return jsonify({"error": "No se pudo completar el registro. Intente nuevamente mas tarde."}), 500

    cursor = conexion.cursor()

    try:
        # 4) Verificar que no exista ya un cliente con el mismo nombre y apellido
        cursor.execute(
            "SELECT id FROM clientes WHERE nombre = %s AND apellido = %s",
            (nombre, apellido)
        )
        if cursor.fetchone():
            return jsonify({
                "error": "Ya existe un cliente registrado con ese nombre y apellido."
            }), 409

        # 5) Insertar el nuevo cliente en la base de datos
        cursor.execute(
            "INSERT INTO clientes (nombre, apellido, telefono, direccion) VALUES (%s, %s, %s, %s)",
            (nombre, apellido, telefono, direccion)
        )
        conexion.commit()

        # Obtener el id generado automaticamente
        id_generado = cursor.lastrowid

        return jsonify({
            "mensaje": "Cliente registrado correctamente.",
            "id": id_generado
        }), 201

    except mysql.connector.Error as error:
        # Igual que arriba: el detalle tecnico queda solo en el log del servidor
        print(f"[ERROR INTERNO] Fallo al procesar el registro: {error}")
        return jsonify({"error": "No se pudo completar el registro. Intente nuevamente mas tarde."}), 500

    finally:
        cursor.close()
        conexion.close()


# ---------------------------------------------------------------------------
# LOGIN: ingreso con usuario y contrasena (tabla usuarios, contrasena con hash)
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET"])
def login():
    if "usuario" in session:
        return redirect(url_for("panel"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def iniciar_sesion():
    usuario = request.form.get("usuario", "").strip()
    password = request.form.get("password", "")

    # Validar que no falte ningun dato
    if not usuario or not password:
        return jsonify({"error": "Ingrese usuario y contrasena."}), 400

    try:
        conexion = obtener_conexion()
    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo de conexion a MySQL: {error}")
        return jsonify({"error": "No se pudo completar el ingreso. Intente nuevamente mas tarde."}), 500

    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT usuario, password_hash FROM usuarios WHERE usuario = %s", (usuario,))
        fila = cursor.fetchone()

        # Mismo mensaje si el usuario no existe o la contrasena es incorrecta,
        # para no revelar cuales usuarios existen
        if not fila or not check_password_hash(fila[1], password):
            return jsonify({"error": "Usuario o contrasena incorrectos."}), 401

        session.clear()
        session["usuario"] = fila[0]
        return jsonify({"mensaje": "Ingreso correcto."}), 200

    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo al procesar el ingreso: {error}")
        return jsonify({"error": "No se pudo completar el ingreso. Intente nuevamente mas tarde."}), 500

    finally:
        cursor.close()
        conexion.close()

@app.route("/logout", methods=["GET"])
def cerrar_sesion():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# MOTOS: cada moto pertenece a un cliente ya registrado (cliente_id -> clientes.id)
# ---------------------------------------------------------------------------

def es_entero(valor):
    # Solo digitos ASCII (evita que caracteres raros pasen como numeros)
    return valor.isascii() and valor.isdigit()

# Ruta que sirve el formulario de registro de motos (frontend)
@app.route("/motos/nueva", methods=["GET"])
@login_requerido
def formulario_motos():
    return render_template("motos.html")

@app.route("/motos", methods=["POST"])
@login_requerido
def registrar_moto():
    # 1) Recibir los datos enviados desde el formulario
    cliente_id = request.form.get("cliente_id", "").strip()
    patente = request.form.get("patente", "").strip()
    marca = request.form.get("marca", "").strip()
    modelo = request.form.get("modelo", "").strip()
    anio = request.form.get("anio", "").strip()

    # 2) Validar que ningun campo obligatorio este vacio
    campos_faltantes = []
    if not cliente_id:
        campos_faltantes.append("cliente_id")
    if not patente:
        campos_faltantes.append("patente")
    if not marca:
        campos_faltantes.append("marca")
    if not modelo:
        campos_faltantes.append("modelo")
    if not anio:
        campos_faltantes.append("anio")

    if campos_faltantes:
        return jsonify({
            "error": "Faltan campos obligatorios.",
            "campos_faltantes": campos_faltantes
        }), 400

    # 3) Validar formatos
    if not es_entero(cliente_id) or int(cliente_id) < 1:
        return jsonify({"error": "El cliente_id debe ser un numero entero positivo."}), 400

    # La patente se guarda en mayusculas y sin espacios ni guiones
    patente = patente.upper().replace(" ", "").replace("-", "")
    if not (patente.isascii() and patente.isalnum() and 5 <= len(patente) <= 10):
        return jsonify({"error": "La patente debe tener entre 5 y 10 letras o numeros."}), 400

    anio_maximo = date.today().year + 1
    if not es_entero(anio) or not (1950 <= int(anio) <= anio_maximo):
        return jsonify({"error": f"El anio debe ser un numero entre 1950 y {anio_maximo}."}), 400

    # Manejo de error si falla la conexion a MySQL (por ejemplo, servidor caido)
    try:
        conexion = obtener_conexion()
    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo de conexion a MySQL: {error}")
        return jsonify({"error": "No se pudo completar el registro. Intente nuevamente mas tarde."}), 500

    cursor = conexion.cursor()

    try:
        # 4) Verificar que el cliente exista
        cursor.execute("SELECT id FROM clientes WHERE id = %s", (int(cliente_id),))
        if not cursor.fetchone():
            return jsonify({"error": "No existe un cliente con ese ID."}), 404

        # 5) Verificar que la patente no este ya registrada
        cursor.execute("SELECT id FROM motos WHERE patente = %s", (patente,))
        if cursor.fetchone():
            return jsonify({"error": "Ya existe una moto registrada con esa patente."}), 409

        # 6) Insertar la moto
        cursor.execute(
            "INSERT INTO motos (cliente_id, patente, marca, modelo, anio) VALUES (%s, %s, %s, %s, %s)",
            (int(cliente_id), patente, marca, modelo, int(anio))
        )
        conexion.commit()

        return jsonify({
            "mensaje": "Moto registrada correctamente.",
            "id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo al procesar el registro de moto: {error}")
        return jsonify({"error": "No se pudo completar el registro. Intente nuevamente mas tarde."}), 500

    finally:
        cursor.close()
        conexion.close()


# ---------------------------------------------------------------------------
# SERVICIOS: cada servicio pertenece a una moto ya registrada (moto_id -> motos.id)
# ---------------------------------------------------------------------------

# Ruta que sirve el formulario de registro de servicios (frontend)
@app.route("/servicios/nueva", methods=["GET"])
@login_requerido
def formulario_servicios():
    return render_template("servicios.html")

@app.route("/servicios", methods=["POST"])
@login_requerido
def registrar_servicio():
    # 1) Recibir los datos enviados desde el formulario
    moto_id = request.form.get("moto_id", "").strip()
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    costo = request.form.get("costo", "").strip()

    # 2) Validar que ningun campo obligatorio este vacio
    campos_faltantes = []
    if not moto_id:
        campos_faltantes.append("moto_id")
    if not fecha:
        campos_faltantes.append("fecha")
    if not descripcion:
        campos_faltantes.append("descripcion")
    if not costo:
        campos_faltantes.append("costo")

    if campos_faltantes:
        return jsonify({
            "error": "Faltan campos obligatorios.",
            "campos_faltantes": campos_faltantes
        }), 400

    # 3) Validar formatos
    if not es_entero(moto_id) or int(moto_id) < 1:
        return jsonify({"error": "El moto_id debe ser un numero entero positivo."}), 400

    # Fecha con formato AAAA-MM-DD, que exista en el calendario, no futura y desde el 2000
    fecha_valida = None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
        try:
            fecha_valida = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            fecha_valida = None
    if fecha_valida is None:
        return jsonify({"error": "La fecha debe tener el formato AAAA-MM-DD y ser una fecha real."}), 400
    if fecha_valida > date.today():
        return jsonify({"error": "La fecha no puede ser futura."}), 400
    if fecha_valida < date(2000, 1, 1):
        return jsonify({"error": "La fecha no puede ser anterior al 01/01/2000."}), 400

    if not (3 <= len(descripcion) <= 200):
        return jsonify({"error": "La descripcion debe tener entre 3 y 200 caracteres."}), 400

    # Costo: acepta coma o punto decimal, sin separador de miles, hasta 2 decimales y mayor a 0
    costo_texto = costo.replace(",", ".")
    if not re.fullmatch(r"\d{1,8}(\.\d{1,2})?", costo_texto) or Decimal(costo_texto) <= 0:
        return jsonify({"error": "El costo debe ser un numero mayor a 0, sin separador de miles y con hasta 2 decimales (ej: 15000 o 15000,50)."}), 400
    costo_valido = Decimal(costo_texto)

    # Manejo de error si falla la conexion a MySQL (por ejemplo, servidor caido)
    try:
        conexion = obtener_conexion()
    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo de conexion a MySQL: {error}")
        return jsonify({"error": "No se pudo completar el registro. Intente nuevamente mas tarde."}), 500

    cursor = conexion.cursor()

    try:
        # 4) Verificar que la moto exista
        cursor.execute("SELECT id FROM motos WHERE id = %s", (int(moto_id),))
        if not cursor.fetchone():
            return jsonify({"error": "No existe una moto con ese ID."}), 404

        # 5) Evitar cargar dos veces el mismo servicio (misma moto, fecha y descripcion)
        cursor.execute(
            "SELECT id FROM servicios WHERE moto_id = %s AND fecha = %s AND descripcion = %s",
            (int(moto_id), fecha_valida.isoformat(), descripcion)
        )
        if cursor.fetchone():
            return jsonify({"error": "Ya existe un servicio igual (misma moto, fecha y descripcion)."}), 409

        # 6) Insertar el servicio
        cursor.execute(
            "INSERT INTO servicios (moto_id, fecha, descripcion, costo) VALUES (%s, %s, %s, %s)",
            (int(moto_id), fecha_valida.isoformat(), descripcion, costo_valido)
        )
        conexion.commit()

        return jsonify({
            "mensaje": "Servicio registrado correctamente.",
            "id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo al procesar el registro de servicio: {error}")
        return jsonify({"error": "No se pudo completar el registro. Intente nuevamente mas tarde."}), 500

    finally:
        cursor.close()
        conexion.close()


# ---------------------------------------------------------------------------
# PANEL: pantalla principal con las motos que estan (o estuvieron) en el taller.
# Cada fila es un servicio (ingreso al taller) con su moto y su dueno.
# ---------------------------------------------------------------------------

# Pantalla del panel (frontend)
@app.route("/panel", methods=["GET"])
@login_requerido
def panel():
    return render_template("panel.html")

def a_datetime(valor):
    # MySQL devuelve datetime; se acepta tambien texto ISO (pruebas con otra base)
    if valor is None or isinstance(valor, datetime):
        return valor
    return datetime.fromisoformat(str(valor))

# Datos del panel en formato JSON (los pide el JavaScript de la pantalla)
@app.route("/panel/datos", methods=["GET"])
@login_requerido
def datos_panel():
    try:
        conexion = obtener_conexion()
    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo de conexion a MySQL: {error}")
        return jsonify({"error": "No se pudo cargar el panel. Intente nuevamente mas tarde."}), 500

    cursor = conexion.cursor()

    try:
        # Primero las motos en proceso y, dentro de cada grupo, las mas recientes
        cursor.execute(
            "SELECT s.id, c.nombre, c.apellido, c.telefono, m.patente, m.marca, m.modelo, "
            "s.descripcion, s.costo, s.ingreso, s.estado, s.retiro "
            "FROM servicios s "
            "JOIN motos m ON m.id = s.moto_id "
            "JOIN clientes c ON c.id = m.cliente_id "
            "ORDER BY (s.estado = 'En proceso') DESC, s.ingreso DESC"
        )
        filas = cursor.fetchall()

        ahora = datetime.now()
        registros = []
        for (sid, nombre, apellido, telefono, patente, marca, modelo,
             descripcion, costo, ingreso, estado, retiro) in filas:
            ingreso = a_datetime(ingreso)
            retiro = a_datetime(retiro)
            fin = retiro or ahora
            registros.append({
                "id": sid,
                "dueno": f"{nombre} {apellido}",
                "telefono": telefono,
                "patente": patente,
                "moto": f"{marca} {modelo}",
                "trabajo": descripcion,
                "monto": float(costo),
                "ingreso": ingreso.strftime("%d/%m/%Y %H:%M"),
                "dias": max((fin.date() - ingreso.date()).days, 0),
                "estado": estado,
                "retiro": retiro.strftime("%d/%m/%Y %H:%M") if retiro else None,
            })

        return jsonify({"registros": registros}), 200

    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo al consultar el panel: {error}")
        return jsonify({"error": "No se pudo cargar el panel. Intente nuevamente mas tarde."}), 500

    finally:
        cursor.close()
        conexion.close()


# Marca un servicio como retirado: pasa a "Completo" y guarda la fecha y hora de retiro.
# La moto y el cliente siguen registrados; solo cambia el estado del servicio.
@app.route("/panel/<int:servicio_id>/completar", methods=["POST"])
@login_requerido
def completar_servicio(servicio_id):
    try:
        conexion = obtener_conexion()
    except mysql.connector.Error as error:
        print(f"[ERROR INTERNO] Fallo de conexion a MySQL: {error}")
        return jsonify({"error": "No se pudo completar la operacion. Intente nuevamente mas tarde."}), 500

    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT estado FROM servicios WHERE id = %s", (servicio_id,))
        fila = cursor.fetchone()
        if fila is None:
            return jsonify({"error": "El servicio indicado no existe."}), 404
        if fila[0] == "Completo":
            return jsonify({"error": "Este servicio ya estaba marcado como completo."}), 409

        cursor.execute(
            "UPDATE servicios SET estado = 'Completo', retiro = %s WHERE id = %s",
            (datetime.now(), servicio_id)
        )
        conexion.commit()
        return jsonify({"mensaje": "Moto retirada. El servicio quedo como Completo."}), 200

    except mysql.connector.Error as error:
        conexion.rollback()
        print(f"[ERROR INTERNO] Fallo al completar el servicio: {error}")
        return jsonify({"error": "No se pudo completar la operacion. Intente nuevamente mas tarde."}), 500

    finally:
        cursor.close()
        conexion.close()



if __name__ == "__main__":
    app.run(debug=True)
