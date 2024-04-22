import sqlite3
conn = sqlite3.connect('bbddminimercadogg.db')
cursor = conn.cursor()
# Nombre de la tabla que quieres visualizar
nombre_tabla = 'productos'

# Obtener los nombres de las columnas
cursor.execute(f"PRAGMA table_info({nombre_tabla})")
column_info = cursor.fetchall()
column_names = [info[1] for info in column_info]

# Imprimir los nombres de las columnas
print("Columnas:")
print(column_names)

# Obtener todos los datos de la tabla
cursor.execute(f"SELECT * FROM {nombre_tabla}")
datos_tabla = cursor.fetchall()

# Imprimir los datos
print("\nDatos:")
for fila in datos_tabla:
    print(fila)

conn.close()
