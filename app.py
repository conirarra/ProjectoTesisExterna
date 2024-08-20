from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import check_password_hash
from database import users, docente

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
    return render_template('asignaturas.html')

@app.route('/docentes')
def docentes():
    page = int(request.args.get('page', 1))  # Obtener el número de página, por defecto es 1
    per_page = 4  # Número de docentes por página
    total_docentes = len(docente)

    # Calcula el inicio y fin de los índices
    start = (page - 1) * per_page
    end = start + per_page

    # Divide los docentes en páginas
    docentes_items = list(docente.items())
    docentes_paginados = dict(docentes_items[start:end])

    # Determina si hay más docentes para mostrar en páginas siguientes
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

if __name__ == '__main__':
    app.run(debug=True)