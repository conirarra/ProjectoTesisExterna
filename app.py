from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.security import check_password_hash
from database import docente_disponibilidad, lista_disponible, lista_usuarios, lista_docentes, docentes_dict, docente_disp_original, update_disponibilidad_csv, jsonify_disponibilidad
from flask_wtf.csrf import CSRFProtect
import csv
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
    return render_template('asignaturas.html', asignaturas=asignaturas)

@app.route('/docentes', methods=['GET', 'POST'])
def mostrar_docentes():
    page = request.args.get('page', 1, type=int)
    per_page = 4
    docentes = list(docente_disponibilidad.keys())
    total_docentes = len(docentes)
    start = (page - 1) * per_page
    end = start + per_page
    lista_docentes = docentes[start:end]

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
                           has_prev=has_prev, has_next=has_next, docentes_dict=docentes_dict)
    
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

@app.route('/generar-horario')
def generar_horario(): 
    return render_template('generar_horario.html')

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
        data = request.json

        docente = data.get('docente')
        ramo = data.get('ramo')
        bloques = data.get('bloques')

        if not docente or not ramo or not bloques:
            return jsonify({'error': 'Faltan datos necesarios'}), 400

        # Guardar datos en secciones.csv
        with open('data/secciones.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            bloques_list = bloques.split(',')  # Convierte la cadena de bloques en una lista
            for bloque in bloques_list:
                writer.writerow([docente, ramo, bloque])

        # Leer el archivo disponibilidad.csv
        disponibilidad_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
        with open('data/disponibilidad.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            encabezado = next(reader)
            for row in reader:
                docente_nombre = row[0]
                for i, dia in enumerate(['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']):
                    for j, bloque in enumerate(['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']):
                        disponibilidad_dict[docente_nombre][dia][bloque] = row[1 + i * 6 + j]

        # Actualizar disponibilidad
        for bloque in bloques.split(','):
            try:
                dia, bloque_hora = bloque.split(' ')
                if docente in disponibilidad_dict:
                    if dia in disponibilidad_dict[docente]:
                        disponibilidad_dict[docente][dia][bloque_hora] = 'No'
            except ValueError as ve:
                print(f"Error al procesar el bloque '{bloque}': {ve}")

        # Guardar cambios en disponibilidad.csv
        update_disponibilidad_csv({}, disponibilidad_dict, file_path='data/disponibilidad.csv')

        return jsonify({'message': 'Datos guardados correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)