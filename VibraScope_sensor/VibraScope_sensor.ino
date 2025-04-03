#include <Adafruit_VL53L0X.h>

// Crea un objeto de la clase Adafruit_VL53L0X
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(1); }
  
  Serial.println("Adafruit VL53L0X - Medición Directa");

  if (!lox.begin()) {
    Serial.println(F("Error al inicializar VL53L0X"));
    while (1);
  }
}

void loop() {
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);  // Ejecuta la medición (bloqueante)

  if (measure.RangeStatus != 4) {  // Medición válida
    // Obtener la lectura directa del sensor
    float currentReading = measure.RangeMilliMeter;

    Serial.print("D:");
    Serial.println(currentReading);
  } else {
    Serial.println("D:-1");
  }
  // No es necesario un delay extra, ya que rangingTest se encarga de esperar la medición.
}
