from werkzeug.security import generate_password_hash

# Diccionario de usuarios predefinidos con contraseñas encriptadas
users = {
    'user1': generate_password_hash('password1'),
    'user2': generate_password_hash('password2')
}

# Lista de asignaturas
asignaturas = [
    'Introducción a las Matemáticas',
    'Cálculo Diferencial',
    'Cálculo Integral',
    'Sistemas y Ecuaciones Diferenciales',
    'Cálculo Avanzado I',
    'Cálculo Avanzado II'
]

# Diccionario de docentes con asignaturas y disponibilidad por día
docente = {
    'Juan Pérez': {
        'asignaturas': ['Cálculo Diferencial', 'Cálculo Integral', 'Cálculo Avanzado I'],
        'disponibilidad': {
            'Lunes': ['1-2', '3-4', '5-6'],
            'Martes': ['1-2', '3-4', '11-12'],
            'Miércoles': ['5-6', '7-8', '11-12'],
            'Jueves': ['1-2', '9-10'],
            'Viernes': ['3-4', '7-8', '11-12']
        }
    },
    'Ana Gómez': {
        'asignaturas': ['Introducción a las Matemáticas', 'Sistemas y Ecuaciones Diferenciales', 'Cálculo Avanzado II'],
        'disponibilidad': {
            'Lunes': ['1-2', '3-4', '11-12'],
            'Martes': ['5-6', '7-8'],
            'Miércoles': ['1-2', '9-10', '11-12'],
            'Jueves': ['3-4', '5-6'],
            'Viernes': ['1-2', '3-4', '11-12']
        }
    },
    'Carlos Fernández': {
        'asignaturas': ['Cálculo Diferencial', 'Cálculo Integral', 'Sistemas y Ecuaciones Diferenciales'],
        'disponibilidad': {
            'Lunes': ['1-2', '3-4', '5-6', '11-12'],
            'Martes': ['3-4', '5-6', '7-8'],
            'Miércoles': ['1-2', '7-8', '9-10'],
            'Jueves': ['1-2', '3-4', '7-8', '11-12'],
            'Viernes': ['5-6', '7-8', '9-10', '11-12']
        }
    },
    'María López': {
        'asignaturas': ['Introducción a las Matemáticas', 'Cálculo Avanzado I', 'Cálculo Avanzado II'],
        'disponibilidad': {
            'Lunes': ['1-2', '3-4', '7-8'],
            'Martes': ['1-2', '3-4'],
            'Miércoles': ['5-6', '9-10', '11-12'],
            'Jueves': ['3-4', '7-8', '9-10'],
            'Viernes': ['1-2', '5-6', '7-8', '11-12']
        }
    },
    'María Fernández': {
        'asignaturas': ['Cálculo Avanzado I', 'Cálculo Integral', 'Sistemas y Ecuaciones Diferenciales'],
        'disponibilidad': {
            'Lunes': ['1-2', '3-4', '5-6', '11-12'],
            'Martes': ['1-2', '3-4', '7-8','11-12'],
            'Miércoles': ['5-6', '9-10'],
            'Jueves': ['3-4', '7-8', '9-10'],
            'Viernes': ['1-2', '5-6']
        }
    }
}

# Diccionario vacío para secciones
secciones = {}

# Función para agregar una sección
def agregar_seccion(profe, asignatura, dia, hora):
    # Verificar si el docente está en la lista de docentes
    if profe not in docente:
        return "Docente no encontrado"
    
    # Verificar si la asignatura está en la lista de asignaturas
    if asignatura not in asignaturas:
        return "Asignatura no válida"
    
    if dia not in docente[profe]['disponibilidad']:
        return "Día no válido"
    
    if hora not in docente[profe]['disponibilidad'][dia]:
        return "Hora no disponible para el día"
    
    # Verificar que la sección no esté ya asignada en el horario especificado
    for seccion in secciones.get(dia, {}).values():
        if hora in seccion['horarios']:
            return "Horario ya ocupado"
    
    if dia not in secciones:
        secciones[dia] = {}
    
    if profe not in secciones[dia]:
        secciones[dia][profe] = {'asignaturas': [], 'horarios': []}
    
    secciones[dia][profe]['asignaturas'].append(asignatura)
    secciones[dia][profe]['horarios'].append(hora)
    
    return "Sección agregada exitosamente"