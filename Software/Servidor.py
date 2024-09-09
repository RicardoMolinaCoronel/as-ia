import asyncio
import struct
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from bleak import BleakClient
import threading
import os
import time
import csv
import signal
import sys

# Direcciones MAC de los dispositivos BLE
address_1 = "FE:4A:B7:91:4F:BF"  # Dirección MAC del primer MCU (Pie Derecho)
address_2 = "D8:5B:A3:30:0C:4D"   # Dirección MAC del segundo MCU (Pie Izquierdo)

# UUID de características para ambos dispositivos
characteristic_uuid_1 = "00002a5d-0000-1000-8000-00805f9b34fb"  # UUID del Pie Derecho
characteristic_uuid_2 = "00002a5d-0000-1000-8000-00805f9b34fb"  # UUID del Pie Izquierdo

# Variables para los datos
x_data_1, y_data_1, z_data_1 = [], [], []  # Sensor Pie Derecho
x_data_2, y_data_2, z_data_2 = [], [], []  # Sensor Pie Izquierdo

timeline = []
sensor_data_list = []
start_time = None

# Estado de toma de datos y etiquetas
is_collecting_data = False
current_label = 0
last_download_click = 0

# Tamaño de la ventana deslizante
WINDOW_SIZE = 150

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='x-axis-graph-1', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='y-axis-graph-1', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='z-axis-graph-1', style={'display': 'inline-block', 'width': '49%'}),
    ]),
    html.Div([
        dcc.Graph(id='x-axis-graph-2', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='y-axis-graph-2', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='z-axis-graph-2', style={'display': 'inline-block', 'width': '49%'}),
    ]),
    html.Div([
        html.Button('Inicio toma de datos', id='start-data-collection', n_clicks=0, style={'margin': '5px'}),
        html.Button('Fin toma de datos', id='stop-data-collection', n_clicks=0, style={'margin': '5px'}),
        html.Button('Inicio CDM', id='start-cdm', n_clicks=0, style={'margin': '5px'}),
        html.Button('Fin CDM', id='stop-cdm', n_clicks=0, style={'margin': '5px'}),
        html.Button('Inicio PVI', id='start-pvi', n_clicks=0, style={'margin': '5px'}),
        html.Button('Fin PVI', id='stop-pvi', n_clicks=0, style={'margin': '5px'}),
        html.Button('Descargar datos', id='download-data', n_clicks=0, style={'margin': '5px'}),
    ], style={'text-align': 'center', 'margin': '20px 0'}),
    dcc.Download(id="download-csv"),
    dcc.Interval(
        id='interval-component',
        interval=50,  # Intervalo en milisegundos 
        n_intervals=0
    )
])

# Variable global para mantener la referencia de los hilos
threads = []
running_ble_clients = {}

@app.callback(
    Output('x-axis-graph-1', 'figure'),
    Output('y-axis-graph-1', 'figure'),
    Output('z-axis-graph-1', 'figure'),
    Output('x-axis-graph-2', 'figure'),
    Output('y-axis-graph-2', 'figure'),
    Output('z-axis-graph-2', 'figure'),
    Output('download-csv', 'data'),
    Input('start-data-collection', 'n_clicks'),
    Input('stop-data-collection', 'n_clicks'),
    Input('start-cdm', 'n_clicks'),
    Input('stop-cdm', 'n_clicks'),
    Input('start-pvi', 'n_clicks'),
    Input('stop-pvi', 'n_clicks'),
    Input('download-data', 'n_clicks'),
    Input('interval-component', 'n_intervals'),
)
def update_graph(start_n_clicks, stop_n_clicks, start_cdm_n_clicks, stop_cdm_n_clicks, start_pvi_n_clicks, stop_pvi_n_clicks, download_n_clicks, n_intervals):
    global is_collecting_data, current_label, timeline, last_download_click, sensor_data_list, start_time

    triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered == 'start-data-collection':
        is_collecting_data = True
        timeline = []  # Reiniciar el timeline
        sensor_data_list = []  # Reiniciar la lista de datos
        start_time = time.time()  # Guardar el tiempo de inicio
    elif triggered == 'stop-data-collection':
        is_collecting_data = False
        stop_all_ble_clients()
    elif triggered == 'start-cdm':
        current_label = 1  # Etiqueta para CDM
    elif triggered == 'stop-cdm':
        if current_label == 1:
            current_label = 0  # Terminar CDM
    elif triggered == 'start-pvi':
        current_label = 2  # Etiqueta para PVI
    elif triggered == 'stop-pvi':
        if current_label == 2:
            current_label = 0  # Terminar PVI

    x_figure_1 = go.Figure()
    y_figure_1 = go.Figure()
    z_figure_1 = go.Figure()

    x_figure_2 = go.Figure()
    y_figure_2 = go.Figure()
    z_figure_2 = go.Figure()

    # Usar la ventana deslizante para graficar los últimos N datos
    x_data_1_window = x_data_1[-WINDOW_SIZE:]
    y_data_1_window = y_data_1[-WINDOW_SIZE:]
    z_data_1_window = z_data_1[-WINDOW_SIZE:]

    x_data_2_window = x_data_2[-WINDOW_SIZE:]
    y_data_2_window = y_data_2[-WINDOW_SIZE:]
    z_data_2_window = z_data_2[-WINDOW_SIZE:]

    if is_collecting_data and len(x_data_1_window) > 0 and len(x_data_2_window) > 0:
        x_figure_1.add_trace(go.Scatter(y=x_data_1_window, mode='lines', name='X (Pie Derecho)', line=dict(color='blue')))
        y_figure_1.add_trace(go.Scatter(y=y_data_1_window, mode='lines', name='Y (Pie Derecho)', line=dict(color='green')))
        z_figure_1.add_trace(go.Scatter(y=z_data_1_window, mode='lines', name='Z (Pie Derecho)', line=dict(color='red')))

        x_figure_2.add_trace(go.Scatter(y=x_data_2_window, mode='lines', name='X (Pie Izquierdo)', line=dict(color='blue')))
        y_figure_2.add_trace(go.Scatter(y=y_data_2_window, mode='lines', name='Y (Pie Izquierdo)', line=dict(color='green')))
        z_figure_2.add_trace(go.Scatter(y=z_data_2_window, mode='lines', name='Z (Pie Izquierdo)', line=dict(color='red')))

        x_figure_1.update_layout(title="Aceleración en el eje X (Pie Derecho)", xaxis_title="Muestra", yaxis_title="Aceleración (m/s²)")
        y_figure_1.update_layout(title="Aceleración en el eje Y (Pie Derecho)", xaxis_title="Muestra", yaxis_title="Aceleración (m/s²)")
        z_figure_1.update_layout(title="Aceleración en el eje Z (Pie Derecho)", xaxis_title="Muestra", yaxis_title="Aceleración (m/s²)")

        x_figure_2.update_layout(title="Aceleración en el eje X (Pie Izquierdo)", xaxis_title="Muestra", yaxis_title="Aceleración (m/s²)")
        y_figure_2.update_layout(title="Aceleración en el eje Y (Pie Izquierdo)", xaxis_title="Muestra", yaxis_title="Aceleración (m/s²)")
        z_figure_2.update_layout(title="Aceleración en el eje Z (Pie Izquierdo)", xaxis_title="Muestra", yaxis_title="Aceleración (m/s²)")

        current_time = time.time()
        timestamp = (current_time - start_time) * 1000  # Tiempo en milisegundos desde el inicio
        timeline.append(timestamp)
        sensor_data_list.append({
            'timestamp': timestamp,
            'x_data_1': x_data_1[-1],
            'y_data_1': y_data_1[-1],
            'z_data_1': z_data_1[-1],
            'x_data_2': x_data_2[-1],
            'y_data_2': y_data_2[-1],
            'z_data_2': z_data_2[-1],
            'current_label': current_label
        })

    csv_data = None
    if triggered == 'download-data':
        if download_n_clicks > last_download_click:
            last_download_click = download_n_clicks
            filename = f'data_{time.strftime("%Y%m%d_%H%M%S")}.csv'
            csv_file_path = os.path.join(os.getcwd(), filename)
            
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'x_data_1', 'y_data_1', 'z_data_1',
                                 'x_data_2', 'y_data_2', 'z_data_2', 'current_label'])
                for data in sensor_data_list:
                    writer.writerow([data['timestamp'], data['x_data_1'], data['y_data_1'], data['z_data_1'],
                                     data['x_data_2'], data['y_data_2'], data['z_data_2'], data['current_label']])
            
            csv_data = dcc.send_file(csv_file_path)

    return (x_figure_1, y_figure_1, z_figure_1, x_figure_2, y_figure_2, z_figure_2, csv_data)


# Variables globales para manejar los fragmentos de datos
partial_data_1 = bytearray()  # Para el primer MCU (Pie Derecho)
partial_data_2 = bytearray()  # Para el segundo MCU (Pie Izquierdo)

async def notification_handler_1(sender, data):
    global partial_data_1
    if is_collecting_data:
        partial_data_1.extend(data)
        if len(partial_data_1) >= 12:
            imu_data = struct.unpack('fff', partial_data_1[:12])
            partial_data_1 = partial_data_1[12:]
            threading.Thread(target=process_data_1, args=(imu_data,)).start()

async def notification_handler_2(sender, data):
    global partial_data_2
    if is_collecting_data:
        partial_data_2.extend(data)
        if len(partial_data_2) >= 12:
            imu_data = struct.unpack('fff', partial_data_2[:12])
            partial_data_2 = partial_data_2[12:]
            threading.Thread(target=process_data_2, args=(imu_data,)).start()

def process_data_1(imu_data):
    global x_data_1, y_data_1, z_data_1
    x_data_1.append(imu_data[0])
    y_data_1.append(imu_data[1])
    z_data_1.append(imu_data[2])
    if len(x_data_1) > WINDOW_SIZE:
        x_data_1.pop(0)
        y_data_1.pop(0)
        z_data_1.pop(0)

def process_data_2(imu_data):
    global x_data_2, y_data_2, z_data_2
    x_data_2.append(imu_data[0])
    y_data_2.append(imu_data[1])
    z_data_2.append(imu_data[2])
    if len(x_data_2) > WINDOW_SIZE:
        x_data_2.pop(0)
        y_data_2.pop(0)
        z_data_2.pop(0)

async def connect_ble(address, characteristic_uuid, handler, loop, retries=5, delay=2):
    for i in range(retries):
        try:
            async with BleakClient(address, loop=loop) as client:
                running_ble_clients[address] = client
                await client.start_notify(characteristic_uuid, handler)
                await asyncio.sleep(3600)
                await client.stop_notify(characteristic_uuid)
                break
        except Exception as e:
            print(f"Error en la conexión BLE {address}: {e}")
            if i < retries - 1:
                print(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
            else:
                print(f"Falló la conexión con {address} después de {retries} intentos.")
        finally:
            print(f"Cerrando la conexión BLE {address}.")
            running_ble_clients.pop(address, None)

def start_ble_connection(address, characteristic_uuid, handler):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_ble(address, characteristic_uuid, handler, loop))

def stop_all_ble_clients():
    for address, client in running_ble_clients.items():
        if client.is_connected:
            asyncio.run_coroutine_threadsafe(client.disconnect(), asyncio.get_event_loop())
    running_ble_clients.clear()

def signal_handler(sig, frame):
    print('Interrupción recibida, cerrando...')
    stop_all_ble_clients()
    for thread in threads:
        if thread.is_alive():
            thread.join(0)
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    dash_thread = threading.Thread(target=lambda: app.run_server(debug=True, use_reloader=False))
    dash_thread.start()
    threads.append(dash_thread)

    ble_thread_1 = threading.Thread(target=start_ble_connection, args=(address_1, characteristic_uuid_1, notification_handler_1))
    ble_thread_1.start()
    threads.append(ble_thread_1)

    ble_thread_2 = threading.Thread(target=start_ble_connection, args=(address_2, characteristic_uuid_2, notification_handler_2))
    ble_thread_2.start()
    threads.append(ble_thread_2)

    dash_thread.join()
    ble_thread_1.join()
    ble_thread_2.join()
