#include <Adafruit_VL53L0X.h>

// Crea un objeto de la clase Adafruit_VL53L0X
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(1); }
  
  Serial.println("Adafruit VL53L0X - Medición Mejorada");

  if (!lox.begin()) {
    Serial.println(F("Error al inicializar VL53L0X"));
    while (1);
  }

  // NOTA: Para aumentar la precisión se suele aumentar el "timing budget".
  // La librería Adafruit no expone directamente una función para ajustarlo,
  // por lo que podrías considerar modificar la librería o usar otra.
}

void loop() {
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);  // Ejecuta la medición (bloqueante)

  if (measure.RangeStatus != 4) {  // Medición válida
    Serial.print("D:");
    Serial.println(measure.RangeMilliMeter);
  } else {
    Serial.println("D:-1");
  }
  // No es necesario un delay extra, ya que rangingTest se encarga de esperar la medición.
}
