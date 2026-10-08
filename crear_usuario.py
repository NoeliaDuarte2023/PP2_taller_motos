# Crea un usuario para ingresar al sistema.
# Se ejecuta una vez por cada usuario nuevo: python crear_usuario.py
import os
import getpass
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()


def main():
    usuario = input("Nombre de usuario: ").strip()
    if len(usuario) < 3:
        print("El usuario debe tener al menos 3 caracteres.")
        return

    # getpass no muestra lo que se escribe (es normal que no se vea nada)
    password = getpass.getpass("Contrasena (no se ve mientras escribis): ")
    repetir = getpass.getpass("Repetir contrasena: ")
    if password != repetir:
        print("Las contrasenas no coinciden. No se creo el usuario.")
        return
    if len(password) < 6:
        print("La contrasena debe tener al menos 6 caracteres.")
        return

    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as error:
        print("No se pudo conectar a MySQL. Verifica que XAMPP este prendido.")
        print(f"[ERROR INTERNO] {error}")
        return

    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
        if cursor.fetchone():
            print("Ese usuario ya existe.")
            return

        # La contrasena se guarda solo como hash, nunca en texto plano
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash) VALUES (%s, %s)",
            (usuario, generate_password_hash(password))
        )
        conexion.commit()
        print("Usuario creado correctamente.")
    except mysql.connector.Error as error:
        print("No se pudo crear el usuario.")
        print(f"[ERROR INTERNO] {error}")
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    main()
