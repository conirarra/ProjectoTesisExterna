import pandas as pd

df_docentes = pd.read_csv('data/docentes.csv')
df_disponible = pd.read_csv('data/disponibilidad.csv')
df_usuarios = pd.read_csv('data/users.csv')

lista_docentes = df_docentes.values.tolist()
lista_disponible = df_disponible.values.tolist()
lista_usuarios = df_usuarios.values.tolist()



