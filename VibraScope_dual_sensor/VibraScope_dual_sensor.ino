// Ejemplo de lectura de dos sensores VL53L0X con ESP32
// Utiliza pines XSHUT para asignar direcciones I2C distintas

#include <Wire.h>
#include <Adafruit_VL53L0X.h>

// Pines XSHUT (ajusta según tu conexión)
#define XSHUT_PIN_1 2
#define XSHUT_PIN_2 4

// Nuevas direcciones I2C (debe ser >= 0x29)
#define SENSOR1_ADDR 0x30
#define SENSOR2_ADDR 0x31

// Objetos VL53L0X
Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(1); }

  // Inicializar I2C
  Wire.begin();

  // Configurar pines XSHUT
  pinMode(XSHUT_PIN_1, OUTPUT);
  pinMode(XSHUT_PIN_2, OUTPUT);

  // Desactivar ambos sensores
  digitalWrite(XSHUT_PIN_1, LOW);
  digitalWrite(XSHUT_PIN_2, LOW);
  delay(10);

  // --- Sensor 1 ---
  digitalWrite(XSHUT_PIN_1, HIGH);
  delay(10);
  if (!lox1.begin()) {
    Serial.println("Error: no se detectó Sensor 1");
    while (1);
  }
  // Cambiar dirección I2C del sensor 1
  if (!lox1.setAddress(SENSOR1_ADDR)) {
    Serial.println("Error al cambiar la dirección del Sensor 1");
    while (1);
  }
  Serial.print("Sensor 1 activo en 0x"); Serial.println(SENSOR1_ADDR, HEX);

  // --- Sensor 2 ---
  digitalWrite(XSHUT_PIN_2, HIGH);
  delay(10);
  if (!lox2.begin()) {
    Serial.println("Error: no se detectó Sensor 2");
    while (1);
  }
  // Cambiar dirección I2C del sensor 2
  if (!lox2.setAddress(SENSOR2_ADDR)) {
    Serial.println("Error al cambiar la dirección del Sensor 2");
    while (1);
  }
  Serial.print("Sensor 2 activo en 0x"); Serial.println(SENSOR2_ADDR, HEX);
}

void loop() {
  VL53L0X_RangingMeasurementData_t m1, m2;

  // Leer Sensor 1
  lox1.rangingTest(&m1, false);
  
  // Leer Sensor 2
  lox2.rangingTest(&m2, false);

  Serial.print("D:");  // Prefijo para reconocer la línea útil
  Serial.print(m1.RangeStatus == 4 ? -1 : m1.RangeMilliMeter);
  Serial.print(",");
  Serial.println(m2.RangeStatus == 4 ? -1 : m2.RangeMilliMeter);

  delay(50);
}
