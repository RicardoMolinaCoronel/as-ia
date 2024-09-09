# CDM

# Guía de Configuración y Uso del Proyecto con Seeed XIAO nRF52840 Sense

## Descripción de los Archivos

### 1. **Datos.py**
Este archivo está diseñado para cargar y graficar datos de un archivo CSV, provenientes del sensor integrado en el MCU Seeed XIAO nRF52840 Sense. Utiliza `pandas` para la manipulación de datos y `matplotlib` para las visualizaciones.

**Funciones Principales:**
- Cargar datos desde un archivo CSV especificado por la ruta `file_path`.
- Graficar los datos de un sensor específico en función del tiempo para los ejes X, Y, y Z.

### 2. **MCU_ACC.ino**
Este archivo es un sketch para la plataforma Arduino que corre en el MCU Seeed XIAO nRF52840 Sense. Está configurado para interactuar con un sensor LSM6DS3 y enviar datos a través de Bluetooth Low Energy (BLE).

**Componentes Usados:**
- **LSM6DS3:** Sensor de movimiento que proporciona datos de aceleración y giroscopio.
- **Bluetooth LE:** Para transmitir datos a dispositivos conectados.

**Configuraciones y Funciones Principales:**
- Inicialización del sensor y configuración para la comunicación I2C.
- Establecimiento de servicios y características BLE para la transmisión de datos.
- Callbacks para manejar conexiones y desconexiones BLE.

**Configuración del MCU:**
Para más información sobre el Seeed XIAO nRF52840 Sense, incluyendo su datasheet y cómo configurarlo en Arduino IDE, visita [esta página](https://wiki.seeedstudio.com/XIAO_BLE/).

### 3. **Servidor.py**
Este archivo implementa un servidor utilizando `Dash` para visualización de datos y `Bleak` para la comunicación con dispositivos BLE. Permite la conexión a dispositivos BLE, recolecta datos y los visualiza en un dashboard web.

**Funciones Principales:**
- Conectarse a dispositivos BLE usando direcciones MAC especificadas.
- Recolectar datos de sensores y visualizarlos en tiempo real.
- Manejar conexiones BLE y el procesamiento de los datos recibidos.

## Instalación de Dependencias

Para ejecutar los scripts correctamente, necesitarás instalar varias bibliotecas de Python y herramientas para Arduino.

### Instalación de Bibliotecas de Python
Ejecuta los siguientes comandos en tu terminal para instalar las bibliotecas necesarias:

```bash
pip install pandas matplotlib dash plotly bleak
```

### Configuración del Entorno de Arduino
1. **Instala Arduino IDE:** Descárgalo desde [Arduino IDE](https://www.arduino.cc/en/software).
2. **Instala las bibliotecas requeridas:**
   - En Arduino IDE, ve a **Herramientas > Administrar Bibliotecas** e instala:
     - `Adafruit Bluefruit nRF52`
     - `SparkFun LSM6DS3`

### Programación del MCU Seeed XIAO nRF52840 Sense
1. Conecta tu MCU a la computadora usando un cable USB.
2. Abre el archivo `MCU_ACC.ino` en Arduino IDE.
3. Selecciona la placa correcta en **Herramientas > Placa > Seeed XIAO nRF52840 Sense**.
4. Selecciona el puerto correcto en **Herramientas > Puerto**.
5. Sube el sketch al MCU.

## Ejecución de los Scripts

### 1. **Ejecución de Datos.py**
Para graficar los datos, asegúrate de tener el archivo CSV disponible en la ruta especificada en el script y luego ejecuta:

```bash
python Datos.py
```

### 2. **Ejecución de Servidor.py**
Para iniciar el servidor de visualización de datos:

```bash
python Servidor.py
```

Este comando iniciará un servidor web que puedes acceder a través de tu navegador para visualizar los datos recolectados desde los dispositivos BLE conectados.

## Conexión y Configuración del Hardware
- **Conexión del LSM6DS3:** Conéctalo a los pines I2C de Seeed XIAO nRF52840 Sense (`SDA` y `SCL`).
- **Bluetooth:** El MCU transmitirá datos a dispositivos habilitados para BLE según esté configurado en el código `MCU_ACC.ino`.

## Notas y Consideraciones
- Asegúrate de que los dispositivos BLE estén encendidos y dentro del rango de conexión.
- Verifica que las direcciones MAC y UUIDs en `Servidor.py` coincidan con los dispositivos que deseas conectar.

