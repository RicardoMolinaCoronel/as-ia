#include <Wire.h>
#include <LSM6DS3.h>
#include <bluefruit.h>

LSM6DS3 myIMU(I2C_MODE, 0x6A);  // Dirección I2C para el sensor LSM6DS3

BLEService imuService = BLEService(0x181A);  
BLECharacteristic imuCharacteristic1 = BLECharacteristic(0x2A5D);

void connect_callback(uint16_t conn_handle) {
  Serial.println("Dispositivo conectado.");
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason) {
  Serial.println("Dispositivo desconectado.");
}

void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando setup...");

  Bluefruit.begin();
  Bluefruit.setName("Pie_derecho");
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);

  Serial.println("Inicializando LSM6DS3...");
  if (myIMU.begin() != 0) {
    Serial.println("Error al inicializar el LSM6DS3");
    while (1);
  } else {
    Serial.println("LSM6DS3 inicializado correctamente");
  }

  // Configurar manualmente la frecuencia de muestreo para el LSM6DS3
  // Establece ODR del acelerómetro a 104 Hz
  myIMU.writeRegister(LSM6DS3_ACC_GYRO_CTRL1_XL, 0x40);
  // Establece ODR del giroscopio a 104 Hz
  myIMU.writeRegister(LSM6DS3_ACC_GYRO_CTRL2_G, 0x40);

  imuService.begin();
  imuCharacteristic1.setProperties(CHR_PROPS_NOTIFY);
  imuCharacteristic1.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  imuCharacteristic1.setFixedLen(12);  // 3 floats (12 bytes)
  imuCharacteristic1.begin();

  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(imuService);
  Bluefruit.Advertising.start();

  Serial.println("Setup completo. Esperando conexión BLE...");
}

void loop() {
  float x_lsm = myIMU.readFloatAccelX();
  float y_lsm = myIMU.readFloatAccelY();
  float z_lsm = myIMU.readFloatAccelZ();

  // Imprimir los valores leídos en el monitor serial
  Serial.print("LSM6DS3 -> X: "); Serial.print(x_lsm);
  Serial.print(", Y: "); Serial.print(y_lsm);
  Serial.print(", Z: "); Serial.println(z_lsm);

  // Convertir los valores a un array de bytes y enviar por BLE
  uint8_t data[12];
  memcpy(data, &x_lsm, 4);
  memcpy(data + 4, &y_lsm, 4);
  memcpy(data + 8, &z_lsm, 4);
  imuCharacteristic1.notify(data, 12);

  delay(10); // Pequeño delay para ajustar el ritmo del loop
}
