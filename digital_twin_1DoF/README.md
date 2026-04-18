# Digital Twin 1DoF

## Proposito

Desarrollar un gemelo digital 3D del sistema masa-resorte vertical de 1 grado de libertad de VibraScope, sincronizado en tiempo real con el movimiento del modelo fisico.

La meta de esta fase no es hacer una simulacion compleja, sino una demo academica robusta donde el modelo virtual replique el desplazamiento medido por el sistema real.

## Referencia

- Referencia visual general: https://www.youtube.com/watch?v=CMVqoBWRyLA
- Base tecnica del proyecto actual: `../VibraScope_1DoF/Paper_ABET.pdf`
- Base de presentacion actual: `../VibraScope_1DoF/PPT VibraScope.pdf`

## Contexto que ya existe

- Sistema 1DoF fisico masa-resorte vertical.
- Sensor `VL53L0X` para medir distancia.
- `ESP32` con salida serial.
- Aplicacion Python actual en `../VibraScope.py`.
- Firmware actual en `../VibraScope_sensor/VibraScope_sensor.ino`.

## Objetivo tecnico de esta fase

Construir una aplicacion Python que:

- lea datos reales desde el `ESP32`;
- convierta distancia absoluta en desplazamiento relativo;
- mueva un modelo 3D sobre el eje vertical;
- permita calibrar cero y escala;
- sea estable para demo de laboratorio.

## Recomendacion tecnica

- Libreria 3D principal recomendada: `PyVista`
- Alternativa para maqueta rapida: `VPython`
- Estrategia sugerida: primero un prototipo 3D simple y luego una version mas fiel al modelo real

## Contrato minimo de datos

Entrada serial esperada:

```text
D:<distancia_en_mm>
```

Ejemplo:

```text
D:123.4
```

Transformaciones minimas:

- set zero;
- conversion a desplazamiento relativo;
- mapeo de mm reales a unidades 3D;
- filtro simple si hay ruido.

## Entregables finales

Al cierre de esta fase se debe entregar:

| Entregable | Descripcion |
| --- | --- |
| Demo funcional | Aplicacion 3D conectada al sistema 1DoF real |
| Codigo fuente | Modulo reproducible y documentado dentro del repo |
| Evidencia | Capturas, video corto y pruebas basicas |
| Paper | Documento tecnico similar a `../VibraScope_1DoF/Paper_ABET.pdf` |
| PPT | Presentacion de resultados similar a `../VibraScope_1DoF/PPT VibraScope.pdf` |

## Criterios de exito

- el modelo 3D responde a datos reales del sensor;
- la masa virtual se mueve sobre el eje correcto;
- la sincronizacion es visualmente estable;
- otra persona puede ejecutar la demo con instrucciones claras;
- el cierre incluye paper y PPT de resultados.

## Cronograma de 8 semanas

| Semana | Objetivo | Tareas principales | Entregable |
| --- | --- | --- | --- |
| 1 | Transferencia y onboarding | Revisar `README`, `VibraScope.py`, firmware y documentos base; entender flujo sensor -> ESP32 -> Python; registrar dudas y riesgos | Nota de onboarding y diagrama de flujo |
| 2 | Definicion funcional | Definir alcance `v0.1`, libreria 3D, sistema de coordenadas, set zero, rango de movimiento y arquitectura minima | Especificacion corta de la solucion |
| 3 | Prototipo 3D inicial | Construir escena 3D simple sin hardware con partes fijas y masa movil; probar animacion simulada | Prototipo 3D local funcionando |
| 4 | Integracion con datos reales | Leer serial real, parsear `D:<valor>`, conectar la masa virtual al dato del sensor y validar movimiento real | Demo conectada al sistema fisico |
| 5 | Calibracion y sincronizacion | Ajustar cero, escala, filtro, estabilidad visual y respuesta temporal; documentar parametros de ajuste | Version calibrada para laboratorio |
| 6 | Interfaz de demo | Agregar selector de puerto, conectar/desconectar, set zero, indicador de estado y modo demo | Version `v0.1` usable por terceros |
| 7 | Validacion y documentacion | Ejecutar pruebas en reposo y movimiento, registrar fallos, documentar instalacion, uso y arquitectura | Reporte de pruebas y guia de uso |
| 8 | Cierre academico | Consolidar demo final, grabar evidencia, redactar paper y preparar PPT de resultados | Demo final, paper y PPT |

## Contenido minimo del paper

El paper debe seguir una estructura similar al documento de `VibraScope_1DoF`:

- titulo y autores;
- problema y motivacion;
- objetivo del gemelo digital;
- metodologia de implementacion;
- arquitectura del sistema;
- integracion sensor -> ESP32 -> Python 3D;
- resultados de sincronizacion;
- limitaciones;
- conclusiones y trabajo futuro.

## Contenido minimo del PPT

La presentacion debe resumir:

- problema identificado;
- objetivo del proyecto;
- arquitectura del sistema;
- stack usado;
- demo del gemelo digital;
- resultados principales;
- dificultades encontradas;
- siguientes pasos.

## Riesgos principales

- ruido en la lectura del sensor;
- latencia alta entre lectura y animacion;
- mala calibracion de cero o escala;
- libreria 3D demasiado pesada para el equipo disponible;
- intentar demasiado detalle visual antes de asegurar sincronizacion.

## Definicion de hecho

Esta fase se considera terminada cuando exista una demo reproducible que muestre el movimiento del modelo 3D sincronizado con el sistema 1DoF fisico, y cuando ese resultado quede documentado en un paper y una PPT.
