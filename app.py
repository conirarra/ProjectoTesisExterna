from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.security import check_password_hash
from database import users, docente, insert_seccion, actualizar_disponibilidad

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

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si el usuario existe y la contraseña es correcta
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('asignaturas'))  # Redirige a asignaturas
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/asignaturas')
def asignaturas():
    return render_template('asignaturas.html', asignaturas=ramos, docente=docente)

@app.route('/docentes', methods=['GET', 'POST'])
def docentes():
    if request.method == 'POST':
        docente_name = request.form.get('docente')
        if docente_name and docente_name in docente:
            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
                horas = request.form.getlist(f'{docente_name}_{dia}')
                # Actualizar disponibilidad en la base de datos
                for hora in horas:
                    actualizar_disponibilidad(docente_name, dia, hora, True)
                # Remover las horas que ya no están disponibles
                horas_actuales = docente[docente_name]['disponibilidad'][dia]
                for hora in horas_actuales:
                    if hora not in horas:
                        actualizar_disponibilidad(docente_name, dia, hora, False)

            flash('Disponibilidad actualizada', 'success')
            return redirect(url_for('docentes'))

    page = int(request.args.get('page', 1))  # Obtener el número de página, por defecto es 1
    per_page = 4  # Número de docentes por página
    total_docentes = len(docente)

    start = (page - 1) * per_page
    end = start + per_page

    docentes_items = list(docente.items())
    docentes_paginados = dict(docentes_items[start:end])

    has_next = end < total_docentes
    has_prev = page > 1

    return render_template(
        'docentes.html', 
        docente=docentes_paginados, 
        page=page, 
        total_docentes=total_docentes,
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev
    )
@app.route('/generar-horario')
def generar_horario(): 
    return render_template('generar_horario.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/add_seccion', methods=['POST'])
def add_seccion():
    data = request.json
    asignatura = data['asignatura']
    seccion = data['seccion']
    horario = data['horario']
    docente = data['docente']

    # Insertar sección en la base de datos
    insert_seccion(asignatura, seccion, horario, docente)

    return jsonify({
        'status': 'success',
        'message': f'Sección {seccion} creada para la asignatura {asignatura} con horario {horario} para el docente {docente}.'
    })

@app.route('/update_disponibilidad', methods=['POST'])
def update_disponibilidad():
    # Lógica para actualizar disponibilidad
    # Aquí recibes la información del formulario y la procesas
    try:
        docente_nombre = request.form.get('docente')
        for key, value in request.form.items():
            if key.startswith(docente_nombre):
                dia, hora = key.split('_')[1], key.split('_')[2]
                nueva_disponibilidad = request.form.get(key) == 'on'
                actualizar_disponibilidad(docente_nombre, dia, hora, nueva_disponibilidad)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error al actualizar disponibilidad: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
    
if __name__ == '__main__':
    app.run(debug=True)