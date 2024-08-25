import mysql.connector as mariadb

try:
    connection = mariadb.connect(host='localhost', port='3306',
                                   user='root', database='depmatematicas')

    if connection:
        cursor = connection.cursor()
    
        cursor.execute("SELECT `Nombre de Usuario`, `Contraseña` FROM users")
        users = {usuario: contraseña for usuario, contraseña in cursor}

        cursor.execute("SELECT `Nombre`, `Asignaturas` FROM docentes")
        docente = {}
        for nombre, asignaturas in cursor:
            docente[nombre] = {
                "asignaturas": asignaturas,
                "disponibilidad": {
                    "Lunes": [],
                    "Martes": [],
                    "Miércoles": [],
                    "Jueves": [],
                    "Viernes": []
                }
            }

        cursor.execute("SELECT `Docente`, `Dia`, `Hora`, `Disponible` FROM disponibilidad")
        for docente_nombre, dia, hora, disponible in cursor:
            if disponible and docente_nombre in docente:
                docente[docente_nombre]["disponibilidad"].setdefault(dia, []).append(hora)

except mariadb.Error as e:
    print(f"Error al conectar a MariaDB: {e}")

finally:
    cursor.close()
    connection.close()

    
def actualizar_disponibilidad(docente_nombre, dia, hora, nueva_disponibilidad):
    try:
        # Establecer la conexión a la base de datos
        connection = mariadb.connect(host='localhost', port=3306,
                                     user='root', database='depmatematicas')
        cursor = connection.cursor()

        # Capitalizar el nombre del día
        dia = dia.capitalize()

        # Insertar o actualizar disponibilidad
        if nueva_disponibilidad:
            cursor.execute("""
                INSERT INTO disponibilidad (Docente, Dia, Hora, Disponible)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE Disponible = VALUES(Disponible)
            """, (docente_nombre, dia, hora, True))
        else:
            cursor.execute("""
                DELETE FROM disponibilidad
                WHERE Docente = %s AND Dia = %s AND Hora = %s
            """, (docente_nombre, dia, hora))

        # Confirmar los cambios
        connection.commit()

        # Actualizar el diccionario docente en memoria
        if docente_nombre in docente:
            if nueva_disponibilidad:
                if hora not in docente[docente_nombre]["disponibilidad"][dia]:
                    docente[docente_nombre]["disponibilidad"][dia].append(hora)
            else:
                if hora in docente[docente_nombre]["disponibilidad"][dia]:
                    docente[docente_nombre]["disponibilidad"][dia].remove(hora)

    except mariadb.Error as e:
        print(f"Error al conectar a MariaDB: {e}")

    finally:
        cursor.close()
        connection.close()

def insert_seccion(asignatura, seccion, horario, docente):
    try:
        connection = mariadb.connect(host='localhost', port='3306',
                                   user='root', database='depmatematicas')
        cursor = connection.cursor()

        query = """
        INSERT INTO secciones (Asignatura, Seccion, Horario, Docente)
        VALUES (%s, %s, %s, %s)
        """
        values = (asignatura, seccion, horario, docente)

        cursor.execute(query, values)
        connection.commit()
    finally:
        cursor.close()
        connection.close()
import pandas as pd

df_docentes = pd.read_csv('data/docentes.csv')
df_disponible = pd.read_csv('data/disponibilidad.csv')
df_usuarios = pd.read_csv('data/users.csv')

lista_docentes = df_docentes.values.tolist()
lista_disponible = df_disponible.values.tolist()
lista_usuarios = df_usuarios.values.tolist()



