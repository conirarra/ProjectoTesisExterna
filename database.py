import pandas as pd
from collections import defaultdict
import csv

df_docentes = pd.read_csv('data/docentes.csv')
df_disponible = pd.read_csv('data/disponibilidad.csv')
df_usuarios = pd.read_csv('data/users.csv')

lista_docentes = df_docentes.values.tolist()
lista_disponible = df_disponible.values.tolist()
lista_usuarios = df_usuarios.set_index('Usuario')['Password'].to_dict()

def load_disponibilidad_csv(file_path='data/disponibilidad.csv'):
    df_disponible = pd.read_csv(file_path)
    
    docente_disponibilidad = defaultdict(lambda: defaultdict(dict))
    
    for index, row in df_disponible.iterrows():
        nombre_docente = row['Nombre']
        
        # Iterar sobre las columnas (que representan "día,bloque")
        for col in df_disponible.columns[1:]:  # omitir la primera columna que es 'Nombre'
            dia, bloque = col.split(',')
            disponibilidad = row[col]  # 'Si' o 'No'
            
            # Asignar la disponibilidad al docente en el diccionario
            docente_disponibilidad[nombre_docente][dia][bloque] = disponibilidad
    
    return dict(docente_disponibilidad)

docente_disponibilidad = load_disponibilidad_csv()
docente_disp_original = docente_disponibilidad.copy()

docentes_dict = {}
for row in lista_docentes:
    nombre = row[0]
    cursos = row[1:]
    docentes_dict[nombre] = cursos

def update_disponibilidad_csv(original_dict, updated_dict, file_path='data/disponibilidad.csv'):
    # Preparar cambios para cada docente
    rows_to_update = []
    
    for docente, dias in updated_dict.items():
        if docente in original_dict:
            fila = [docente]
            for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']:
                for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']:
                    # Obtener el estado actualizado
                    new_status = dias.get(dia, {}).get(bloque, 'No')
                    # Agregar el estado a la fila
                    fila.append(new_status)
            
            rows_to_update.append(fila)

    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Escribir el encabezado
        encabezado = ['Nombre'] + [f"{dia},{bloque}" for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes'] for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']]
        writer.writerow(encabezado)
        
        # Escribir las filas actualizadas
        for row in rows_to_update:
            writer.writerow(row)

def jsonify_disponibilidad(docente_disponibilidad):
    result = {}
    for docente, disponibilidad in docente_disponibilidad.items():
        disponibilidad_simple = {}
        for dia, horarios in disponibilidad.items():
            disponibilidad_simple[dia] = [horario for horario, estado in horarios.items()]
        result[docente] = disponibilidad_simple
    return result

def leer_secciones_csv():
    secciones = []
    with open('data/secciones.csv', mode='r', encoding='utf-8') as archivo:
        lector_csv = csv.DictReader(archivo)
        for fila in lector_csv:
            secciones.append(fila)
    return secciones

print(docente_disponibilidad)