# Librerias necesarias
from flask import Flask, request, jsonify, render_template
import mysql.connector
import os
from dotenv import load_dotenv

# Cargar las variables definidas en el archivo .env
load_dotenv()

app = Flask(__name__)

# Funcion para obtener la conexion a la base de datos MySQL
# Las credenciales se leen desde variables de entorno (archivo .env)
def obtener_conexion():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Ruta que sirve el formulario de registro de clientes (frontend)
@app.route("/", methods=["GET"])
def formulario_clientes():
    return render_template("formulario.html")

@app.route("/clientes", methods=["POST"])
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


if __name__ == "__main__":
    app.run(debug=True)
