import json

# Nombre del archivo de entrada y salida
archivo_entrada = 'Datos_recogidos/data_20241028_141639.json'
archivo_salida = 'datos_filtrados.json'

# Leer los datos desde el archivo JSON
with open(archivo_entrada, 'r') as f:
    data = json.load(f)

# Función para filtrar registros
def filtrar_registros(data):
    for key in ["derecha", "izquierda"]:
        # Filtramos solo los registros que contienen 'x', 'y' y 'z'
        data[key] = [item for item in data[key] if all(k in item for k in ["x", "y", "z", "a", "b", "g", "t", "millis"])]
    return data

# Filtrar los datos
data_filtrada = filtrar_registros(data)

# Guardar los datos filtrados en un nuevo archivo JSON
with open(archivo_salida, 'w') as f:
    json.dump(data_filtrada, f, indent=4)

print(f"Datos filtrados guardados en {archivo_salida}")