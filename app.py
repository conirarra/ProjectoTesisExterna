from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.security import check_password_hash
from database import docente_disponibilidad, lista_disponible, lista_usuarios, lista_docentes, docentes_dict, docente_disp_original, update_disponibilidad_csv, jsonify_disponibilidad
from flask_wtf.csrf import CSRFProtect
import csv

ramos = [
    'Introducción a las Matemáticas',
    'Cálculo Diferencial',
    'Cálculo Integral',
    'Sistemas y Ecuaciones Diferenciales',
    'Cálculo Avanzado I',
    'Cálculo Avanzado II'
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
            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
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
                           disponibilidad=docente_disponibilidad, dias=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
                           bloques=['1-2', '3-4', '5-6', '7-8', '9-10', '11-12'],
                           page=page, total_docentes=total_docentes, per_page=per_page,
                           has_prev=has_prev, has_next=has_next, docentes_dict=docentes_dict)

def manage_docentes():
    if request.method == 'GET':
        # Obtener la lista de docentes
        docentes = list(docente_disponibilidad.keys())
        return jsonify(docentes)
    elif request.method == 'POST':
        # Manejar la creación o modificación de secciones (esto es solo un ejemplo, ajusta según tus necesidades)
        data = request.form
        asignatura = data.get('asignatura')
        docente = data.get('docente')
        horario = data.get('horario')
        # Aquí puedes agregar la lógica para manejar la creación de secciones
        return 'Sección creada', 200
    
@app.route('/disponibilidad/<docente>', methods=['GET'])
def get_disponibilidad(docente):
    # Retorna la disponibilidad de un docente específico
    disponibilidad_simple = jsonify_disponibilidad(docente_disponibilidad)
    horarios = disponibilidad_simple.get(docente, {})
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

if __name__ == '__main__':
    app.run(debug=True)