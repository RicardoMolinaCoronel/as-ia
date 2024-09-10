import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV
file_path = 'C:\\Users\\Aldahir\\Desktop\\TESIS 2\\data_20240828_222607.csv'  # Reemplaza con la ruta a tu archivo
data = pd.read_csv(file_path)

# Función para graficar los datos de un sensor específico
def plot_sensor_data(ax, timestamp, x_data, y_data, z_data, label, sensor_name):
    ax.plot(timestamp, x_data, label=f'{sensor_name} - X')
    ax.plot(timestamp, y_data, label=f'{sensor_name} - Y')
    ax.plot(timestamp, z_data, label=f'{sensor_name} - Z')

    # Resaltar los puntos donde current_label es 1 o 2 con diferentes colores
    label_1_idx = label == 1
    label_2_idx = label == 2

    ax.scatter(timestamp[label_1_idx], x_data[label_1_idx], color='red', marker='o', label='Label 1')
    ax.scatter(timestamp[label_1_idx], y_data[label_1_idx], color='red', marker='o')
    ax.scatter(timestamp[label_1_idx], z_data[label_1_idx], color='red', marker='o')

    ax.scatter(timestamp[label_2_idx], x_data[label_2_idx], color='blue', marker='o', label='Label 2')
    ax.scatter(timestamp[label_2_idx], y_data[label_2_idx], color='blue', marker='o')
    ax.scatter(timestamp[label_2_idx], z_data[label_2_idx], color='blue', marker='o')

    ax.set_title(f'{sensor_name} Data')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Acceleration')
    ax.legend()

# Crear subplots para cada sensor en ambos pies
fig, axs = plt.subplots(2, 1, figsize=(14, 10))

# Graficar pie derecho - Sensor LSM
plot_sensor_data(axs[0], data['timestamp'], data['x_data_1'], data['y_data_1'], data['z_data_1'], data['current_label'], 'Right Foot - LSM')

# Graficar pie izquierdo - Sensor LSM
plot_sensor_data(axs[1], data['timestamp'], data['x_data_2'], data['y_data_2'], data['z_data_2'], data['current_label'], 'Left Foot - LSM')

plt.tight_layout()
plt.show()
