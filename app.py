from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.security import check_password_hash
from database import docente_disponibilidad, lista_disponible, lista_usuarios, lista_docentes, docentes_dict, docente_disp_original, update_disponibilidad_csv, jsonify_disponibilidad, leer_secciones_csv
from flask_wtf.csrf import CSRFProtect
import csv
import os
from collections import defaultdict

ramos = [
    'Introduccion a las Matematicas',
    'Calculo Diferencial',
    'Calculo Integral',
    'Sistemas y Ecuaciones Diferenciales',
    'Calculo Avanzado I',
    'Calculo Avanzado II'
]

app = Flask(__name__)
app.secret_key = 'your_secret_key'
csrf = CSRFProtect(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si el usuario existe y la contraseña es correcta
        if username in lista_usuarios and check_password_hash(lista_usuarios[username], password):
            session['username'] = username
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('asignaturas'))  # Redirige a asignaturas
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/asignaturas')
def asignaturas():
    asignaturas = {ramo: [] for ramo in ramos}
    secciones = leer_secciones_csv()
    for seccion in secciones:
        ramo = seccion['ramo']
        if ramo in asignaturas:
            asignaturas[ramo].append(seccion)
    return render_template('asignaturas.html', asignaturas=asignaturas, secciones=secciones)

@app.route('/docentes', methods=['GET', 'POST'])
def mostrar_docentes():
    page = request.args.get('page', 1, type=int)
    per_page = 4
    docentes = list(docente_disponibilidad.keys())
    total_docentes = len(docentes)
    start = (page - 1) * per_page
    end = start + per_page
    lista_docentes = docentes[start:end]
    secciones = leer_secciones_csv()

    has_prev = page > 1
    has_next = end < total_docentes

    if request.method == 'POST':
        docente = request.form.get('docente')
        if docente in docente_disponibilidad:
            for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']:
                for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']:
                    key = f"{docente}_{dia}_{bloque}"
                    if request.form.get(key):
                        if bloque not in docente_disponibilidad[docente][dia]:
                            docente_disponibilidad[docente][dia][bloque] = 'Si'
                    else:
                        if bloque in docente_disponibilidad[docente][dia]:
                            docente_disponibilidad[docente][dia][bloque] = 'No'

        flash('Cambios guardados con éxito', 'success')
        return redirect(url_for('mostrar_docentes', page=page))

    return render_template('docentes.html', lista_docentes=lista_docentes,
                           disponibilidad=docente_disponibilidad, dias=['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes'],
                           bloques=['1-2', '3-4', '5-6', '7-8', '9-10', '11-12'],
                           page=page, total_docentes=total_docentes, per_page=per_page,
                           has_prev=has_prev, has_next=has_next, docentes_dict=docentes_dict, secciones=secciones)
    
@app.route('/get_disponibilidad/<docente>', methods=['GET'])
def get_disponibilidad(docente):
    print(f'Recibiendo solicitud para docente: {docente}')
    if docente not in docente_disponibilidad:
        print('Docente no encontrado')
        return jsonify({'error': 'Docente no encontrado'}), 404
    horarios = docente_disponibilidad[docente]
    return jsonify(horarios)

@app.route('/get_docentes', methods=['GET'])
def get_docentes():
    ramo = request.args.get('ramo')  # Obtener el ramo de los parámetros de consulta
    if not ramo:
        return jsonify({'docentes': []})

    # Filtrar docentes que imparten el ramo
    docentes_que_imparten_ramo = [docente for docente, ramos in docentes_dict.items() if ramo in ramos]
    
    return jsonify({'docentes': docentes_que_imparten_ramo})

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/update_docentes', methods=['POST'])
def update_docentes():
    try:
        docentes_data = request.get_json()
        print(f'Datos recibidos: {docentes_data}')

        if not docentes_data:
            raise ValueError("No se recibieron datos")

        original_dict = docente_disp_original
        print(f'Estado original del diccionario: {original_dict}')

        for docente, dias in docentes_data.items():
            if docente in original_dict:
                original_dict[docente].update(dias)
            else:
                original_dict[docente] = dias

        print(f'Estado actualizado del diccionario: {original_dict}')

        update_disponibilidad_csv(original_dict, original_dict)

        return jsonify({'success': True})

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400
    
@app.route('/guardar_datos', methods=['POST'])
def guardar_datos():
    try:
        # Obtener los datos JSON del request
        data = request.json

        # Verificar que los datos sean una lista
        if not isinstance(data, list):
            return jsonify({'error': 'Datos no están en el formato esperado'}), 400
        
        next_id = get_next_id("data/secciones.csv")

        for item in data:
            item['id'] = next_id
            next_id += 1
        
        docentes = set()
        ramos = set()
        bloques = []

        # Procesar los datos recibidos
        for item in data:
            docente = item.get('docente')
            ramo = item.get('ramo')
            dia = item.get('dia')
            bloque = item.get('bloque')
            id = item.get('id')

            if not docente or not ramo or not dia or not bloque:
                return jsonify({'error': 'Faltan datos necesarios'}), 400

            docentes.add(docente)
            ramos.add(ramo)

            # Añadir el bloque a la lista de bloques
            bloques.append({'id': id, 'dia': dia, 'bloque': bloque, 'docente': docente, 'ramo': ramo})

        # Guardar datos en secciones.csv
        with open('data/secciones.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'docente', 'ramo', 'dia', 'bloque'])
            # Si el archivo está vacío, escribe el encabezado
            if file.tell() == 0:
                writer.writeheader()
            # Escribir las filas
            for item in bloques:
                writer.writerow(item)

        # Leer el archivo disponibilidad.csv y actualizar disponibilidad
        disponibilidad_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
        try:
            with open('data/disponibilidad.csv', mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                encabezado = next(reader)
                for row in reader:
                    docente_nombre = row[0]
                    for i, dia in enumerate(['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']):
                        for j, bloque in enumerate(['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']):
                            disponibilidad_dict[docente_nombre][dia][bloque] = row[1 + i * 6 + j]
        except FileNotFoundError:
            print("Archivo disponibilidad.csv no encontrado, creando nuevo.")

        # Actualizar disponibilidad en el diccionario
        for item in bloques:
            dia = item.get('dia')
            bloque_hora = item.get('bloque')
            docente = item.get('docente')
            if docente in disponibilidad_dict:
                if dia in disponibilidad_dict[docente]:
                    disponibilidad_dict[docente][dia][bloque_hora] = 'No'

        # Guardar cambios en disponibilidad.csv
        with open('data/disponibilidad.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Escribir el encabezado
            writer.writerow(['Nombre',
                             'Lunes,1-2', 'Lunes,3-4', 'Lunes,5-6', 'Lunes,7-8', 'Lunes,9-10', 'Lunes,11-12',
                             'Martes,1-2', 'Martes,3-4', 'Martes,5-6', 'Martes,7-8', 'Martes,9-10', 'Martes,11-12',
                             'Miercoles,1-2', 'Miercoles,3-4', 'Miercoles,5-6', 'Miercoles,7-8', 'Miercoles,9-10', 'Miercoles,11-12',
                             'Jueves,1-2', 'Jueves,3-4', 'Jueves,5-6', 'Jueves,7-8', 'Jueves,9-10', 'Jueves,11-12',
                             'Viernes,1-2', 'Viernes,3-4', 'Viernes,5-6', 'Viernes,7-8', 'Viernes,9-10', 'Viernes,11-12'])

            # Escribir las filas
            for docente, dias in disponibilidad_dict.items():
                row = [docente]
                for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']:
                    for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']:
                        row.append(disponibilidad_dict[docente][dia][bloque])
                writer.writerow(row)

        return jsonify({'message': 'Datos guardados correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/generar_horario')
def generar_horario():
    docentes = [{'id': i+1, 'nombre': d[0], 'ramos': d[1:]} for i, d in enumerate(lista_docentes)]
    return render_template('generar_horario.html', docentes=docentes)

@app.route('/get_ramos/<int:docente_id>')
def get_ramos(docente_id):
    docente = next((d for d in lista_docentes if lista_docentes.index(d) + 1 == docente_id), None)
    if docente:
        return jsonify({"ramos": docente[1:]})
    return jsonify({"ramos": []})

@app.route('/obtener_horario', methods=['POST'])
def obtener_horario():
    data = request.json  # Lee los datos enviados desde el frontend
    docente = data.get('docente')
    ramo = data.get('ramo')
    secciones = leer_secciones_csv()

    # Filtrar las secciones que coincidan con el docente y el ramo seleccionados
    secciones_filtradas = [seccion for seccion in secciones if seccion['docente'] == docente and seccion['ramo'] == ramo]

    return jsonify({'secciones': secciones_filtradas})

@app.route('/eliminar_seccion', methods=['POST'])
def eliminar_seccion():
    data = request.get_json()
    ramo = data.get('ramo')
    docente = data.get('docente')
    dia = data.get('dia')
    bloque = data.get('bloque')

    # Leer el archivo CSV
    try:
        with open("data/secciones.csv", mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader if not (row['docente'] == docente and row['dia'] == dia and row['bloque'] == bloque and row['ramo'] == ramo)]

        # Escribir el archivo CSV actualizado
        with open("data/secciones.csv", mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'docente', 'ramo', 'dia', 'bloque']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return jsonify(success=True)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(success=False)
    
def get_next_id(filename):
    """Obtiene el siguiente id disponible basado en el número de filas en el archivo CSV."""
    if not os.path.isfile(filename):
        return 1  # Si el archivo no existe, empezamos con el id 1
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        ids = [int(row['id']) for row in reader if row['id'].isdigit()]
        return max(ids, default=0) + 1

if __name__ == '__main__':
    app.run(debug=True)