import mariadb

try:
    connection = mariadb.connect(host='localhost', user='root', password='password', database='depmatematicas')

    if connection:
        cursor = connection.cursor()
    
        # Cargar datos de la tabla users
        cursor.execute("SELECT `Nombre de Usuario`, `Contraseña` FROM users")
        users = {usuario: contraseña for usuario, contraseña in cursor}

        # Cargar datos de la tabla docentes
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

        # Cargar datos de la tabla disponibilidad
        cursor.execute("SELECT `Docente`, `Dia`, `Hora`, `Disponibilidad` FROM disponibilidad")
        for docente_nombre, dia, hora, disponible in cursor:
            if disponible and docente_nombre in docente:
                docente[docente_nombre]["disponibilidad"][dia].append(hora)

except mariadb.Error as e:
    print(f"Error al conectar a MariaDB: {e}")

finally:
    if connection:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")

def actualizar_disponibilidad(docente_nombre, dia, hora, nueva_disponibilidad):
    try:
        connection = mariadb.connect(host='localhost', user='root', password='password', database='depmatematicas')
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE disponibilidad
            SET Disponibilidad = ?
            WHERE Docente = ? AND Dia = ? AND Hora = ?
        """, (nueva_disponibilidad, docente_nombre, dia, hora))

        # Confirmar los cambios en la base de datos
        connection.commit()

        # Capitalizar el día para asegurarse de que coincide con las llaves del diccionario
        dia = dia.capitalize()

        # Actualizar el diccionario docente
        if docente_nombre in docente:
            if nueva_disponibilidad == False:
                # Remover la hora de la lista de disponibilidad si se establece como False
                if hora in docente[docente_nombre]["disponibilidad"][dia]:
                    docente[docente_nombre]["disponibilidad"][dia].remove(hora)
            else:
                # Agregar la hora de la lista de disponibilidad si se establece como True
                if hora not in docente[docente_nombre]["disponibilidad"][dia]:
                    docente[docente_nombre]["disponibilidad"][dia].append(hora)
                    
    except mariadb.Error as e:
        print(f"Error al conectar a MariaDB: {e}")

    finally:
        cursor.close()

def insert_seccion(asignatura, seccion, horario, docente):
    try:
        connection = mariadb.connect(host='localhost', user='root', password='password', database='depmatematicas')
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