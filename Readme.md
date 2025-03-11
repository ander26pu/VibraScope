# VibraScope - Equipo de laboratorio

Sistema para digitalizar modelos masa-resorte-amortiguador en laboratorios educativos de vibraciones mecánicas.

## 📋 Descripción
VibraScope permite:
- Capturar **movimientos en tiempo real** de modelos físicos mediante sensores de distancia
- Visualizar la posición vs tiempo de sistemas vibratorios
- Analizar datos para comparar con modelos teóricos
- Ideal para cursos prácticos de dinámica y vibraciones

## 🎛 Componentes
### Hardware
- Microcontrolador ESP32
- Sensor de distancia láser VL53L0X (1+ unidades)
- Protoboard y cables Dupont
- Fuente de alimentación USB
- Modelo físico (ej. masa-resorte)

### Software
- Arduino IDE (para programar ESP32)
- Python 3.7+ con:
  ```bash
  pip install pyserial matplotlib numpy
  ```
## 🔌 Configuración
### Conexión Electrónica
1. Conectar los sensores VL53L0X al ESP32: 
    ```
    VIN -> 3.3V
    GND -> GND
    SDA -> GPIO21
    SCL -> GPIO22
    ```
2. Repetir para múltiples sensores (usando pines XSHUT diferentes)

### Programación
1. Cargar el firmware al ESP32

## 📊 Uso del Software
Ejecutar la aplicación Python:
```
python vibrascope.py --port COM3  # Windows
python vibrascope.py --port /dev/ttyUSB0  # Linux
```

2. Próximas características de la interfaz:
- Gráfico en tiempo real de posición
- Control de escala y eje temporal
- Exportar datos a CSV
- Comparación con modelos teóricos

## 🖼️ Interfaz Gráfica
Captura de interfaz <!-- Agregar captura real -->

## 📚 Recursos Educativos (próximamente)
Ejercicios sugeridos:

Comparación amortiguado vs no amortiguado

Cálculo de frecuencia natural

Verificación de relación masa-desplazamiento

## ⚖️ Licencia
Licencia MIT - Ver LICENSE para detalles.

Desarrollado para laboratorios educativos - Contribuciones y sugerencias bienvenidas.