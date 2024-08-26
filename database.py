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
        
        # Extraer los bloques y disponibilidad, comenzando desde la segunda columna
        bloques_disponibles = row[1:].dropna().values
        
        for i in range(0, len(bloques_disponibles) - 1, 2):
            dia = bloques_disponibles[i]
            bloque = bloques_disponibles[i + 1]
            disponible = bloques_disponibles[i + 2] if (i + 2) < len(bloques_disponibles) else 'No'
            
            # Verifica que 'dia', 'bloque' y 'disponible' no sean NaN
            if pd.notna(dia) and pd.notna(bloque):
                docente_disponibilidad[nombre_docente][dia][bloque] = disponible
    
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
            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
                for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']:
                    # Obtener el estado actualizado
                    new_status = dias.get(dia, {}).get(bloque, 'No')
                    # Agregar el estado a la fila
                    fila.append(new_status)
            
            rows_to_update.append(fila)

    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Escribir el encabezado
        encabezado = ['Nombre'] + [f"{dia},{bloque}" for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']]
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
