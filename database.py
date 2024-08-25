import pandas as pd
from collections import defaultdict
import csv

df_docentes = pd.read_csv('data/docentes.csv')
df_disponible = pd.read_csv('data/disponibilidad.csv')
df_usuarios = pd.read_csv('data/users.csv')

lista_docentes = df_docentes.values.tolist()
lista_disponible = df_disponible.values.tolist()
lista_usuarios = df_usuarios.set_index('Usuario')['Password'].to_dict()

docente_disponibilidad = defaultdict(lambda: defaultdict(dict))
for disponibilidad in lista_disponible:
    nombre_docente = disponibilidad[0]
    dia_semana = disponibilidad[1]
    bloques = disponibilidad[2:]

    for i in range(0, len(bloques), 2):
        bloque = bloques[i]
        disponible = bloques[i + 1]
        docente_disponibilidad[nombre_docente][dia_semana][bloque] = disponible

docente_disponibilidad = dict(docente_disponibilidad)
docente_disp_original = docente_disponibilidad.copy()

docentes_dict = {}
for row in lista_docentes:
    nombre = row[0]
    cursos = row[1:]
    docentes_dict[nombre] = cursos

def update_disponibilidad_csv(original_dict, updated_dict, file_path='data/disponibilidad.csv'):
    rows_to_update = []
    
    # Preparar cambios para cada docente
    for docente, dias in updated_dict.items():
        if docente in docente_disp_original:
            changes = []
            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
                for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']:
                    new_status = dias.get(dia, {}).get(bloque, 'No')
                    old_status = docente_disp_original[docente].get(dia, {}).get(bloque, 'No')
                    if new_status != old_status:
                        changes.append((dia, bloque, new_status))

            if changes:
                fila = [docente]
                for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
                    for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']:
                        if (dia, bloque, dias.get(dia, {}).get(bloque, 'No')) in changes:
                            fila.append(dias[dia].get(bloque, 'No'))
                        else:
                            fila.append(docente_disp_original[docente].get(dia, {}).get(bloque, 'No'))
                rows_to_update.append(fila)

    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Escribir el encabezado
        encabezado = ['Nombre'] + [f"{dia}_{bloque}" for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] for bloque in ['1-2', '3-4', '5-6', '7-8', '9-10', '11-12']]
        encabezado = [f"{b},{d}" for b in encabezado for d in ['Disponible']]  # Actualizar para reflejar el formato Bloque,Disponible
        writer.writerow(encabezado)
        
        # Escribir las filas actualizadas
        for row in rows_to_update:
            writer.writerow(row)


