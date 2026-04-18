# Digital Twin 1DoF

## Proposito

Este directorio define el siguiente proyecto de VibraScope: construir un gemelo digital 3D del sistema masa-resorte vertical de 1 grado de libertad, sincronizado en tiempo real con el movimiento del modelo fisico.

La idea central es que el prototipo fisico siga siendo la fuente real de datos y que un modelo 3D en Python replique su desplazamiento vertical casi en tiempo real, de forma visual, estable y demostrable en laboratorio.

## Referencia del proyecto

Referencia visual compartida por el equipo:

- https://www.youtube.com/watch?v=CMVqoBWRyLA

Nota:

- Este proyecto toma el video como referencia funcional y visual general.
- El objetivo inmediato no es copiar toda la presentacion del video, sino lograr una primera version robusta del gemelo digital del sistema 1DoF ya construido.

## Resultado esperado

Al final de esta etapa, se espera tener una aplicacion Python capaz de:

- leer en tiempo real la distancia medida por el sensor del sistema fisico;
- convertir esa medicion en desplazamiento vertical util;
- mover un modelo 3D simplificado del equipo de forma sincronizada;
- permitir calibracion basica de cero y escala;
- mostrar una demo estable para uso academico y de laboratorio.

## Contexto que la nueva integrante debe heredar

La nueva integrante no debe empezar desde cero. Debe recibir el contexto tecnico ya construido en el repositorio.

### Archivos clave del proyecto actual

- `../Readme.md`
- `../VibraScope.py`
- `../VibraScope_sensor/VibraScope_sensor.ino`
- `../VibraScope_1DoF/Paper_ABET.pdf`
- `../VibraScope_1DoF/PPT VibraScope.pdf`

### Lo que ya existe

- Un modelo experimental 1DoF masa-resorte vertical.
- Un sensor `VL53L0X` para medicion de distancia.
- Un `ESP32` que envia datos por puerto serial.
- Una interfaz Python para visualizacion en tiempo real.
- Una base experimental validada para el sistema 1DoF.

### Lo que falta construir

- Un modulo 3D independiente o integrable con la app actual.
- Un modelo virtual alineado con la geometria real del montaje.
- Una capa de sincronizacion entre lectura serial y animacion 3D.
- Procedimientos de calibracion y validacion del gemelo digital.

## Recomendacion tecnica inicial

### Libreria 3D sugerida

Se recomienda comenzar con `PyVista` para la primera implementacion.

### Motivo de la recomendacion

- Permite trabajar con mallas y escenas 3D de forma relativamente directa.
- Tiene una curva razonable para prototipado tecnico.
- Encaja mejor con una representacion de piezas y geometria que una animacion puramente academica con primitivas.
- Tiene ejemplos claros de animacion y manejo de actores.

### Alternativa valida para una prueba rapida

`VPython` puede usarse si el objetivo es hacer primero una maqueta 3D muy simple con cilindros, resortes y masas basicas antes de pasar a un modelo mas fiel.

### Decision sugerida

- Fase 1: prueba de concepto con una escena simple.
- Fase 2: migrar o consolidar sobre `PyVista` con un modelo mas cercano al equipo real.

## Alcance de esta fase

### Dentro del alcance

- Sincronizar el desplazamiento vertical del modelo 3D con el sistema fisico 1DoF.
- Mostrar movimiento en tiempo real del bloque o masa principal.
- Tener una escena navegable y entendible.
- Medir estabilidad de la sincronizacion.
- Documentar el proceso para que otra persona pueda continuarlo.

### Fuera del alcance por ahora

- Simular dinamica fisica propia del gemelo sin datos reales.
- Hacer un gemelo digital completo de 2DoF.
- Incluir realidad aumentada o realidad virtual.
- Reconstruccion 3D avanzada con escaneo o fotogrametria.
- Analitica avanzada en nube o dashboards web.

## Contrato minimo de datos

La primera version debe apoyarse en el formato actual ya usado por el proyecto.

### Entrada esperada

- Puerto serial del `ESP32`.
- Trama actual de lectura simple:

```text
D:<distancia_en_mm>
```

Ejemplo:

```text
D:123.4
```

### Transformacion esperada

- convertir distancia absoluta en desplazamiento relativo;
- permitir fijar un cero de referencia;
- mapear milimetros reales a unidades de escena 3D;
- limitar valores fuera de rango;
- suavizar ruido si fuera necesario.

### Salida esperada

- posicion vertical del actor 3D correspondiente a la masa movil;
- actualizacion visual estable;
- opcion de mostrar el valor numerico actual en pantalla.

## Arquitectura sugerida

Para reducir riesgo, se recomienda separar el trabajo en capas.

### Capa 1: adquisicion

- lectura serial;
- validacion de datos;
- manejo de desconexion o datos invalidos.

### Capa 2: procesamiento

- calibracion de cero;
- filtro o suavizado;
- conversion a desplazamiento relativo;
- normalizacion de escala.

### Capa 3: escena 3D

- carga o construccion del modelo;
- separacion entre partes fijas y partes moviles;
- animacion del eje vertical.

### Capa 4: interfaz minima

- seleccion de puerto;
- boton conectar/desconectar;
- boton set zero;
- indicador de conexion;
- indicador de valor actual;
- boton iniciar demo.

## Criterios de exito del proyecto

La fase se considerara exitosa si se cumple lo siguiente:

- el modelo 3D responde a datos reales del sensor;
- la masa virtual se mueve sobre el eje correcto;
- el retraso visual es bajo y no rompe la experiencia de demo;
- la aplicacion puede ser ejecutada por otra persona con instrucciones claras;
- existe evidencia de validacion basica con pruebas documentadas.

## Plan de trabajo detallado de 8 semanas

## Semana 1 - Transferencia de conocimiento y aterrizaje tecnico

### Objetivo

Lograr que la nueva integrante entienda que existe hoy, como funciona el prototipo 1DoF y cual es el objetivo del gemelo digital.

### Tareas

- Leer el `README` principal del repositorio.
- Revisar el documento tecnico en `VibraScope_1DoF/Paper_ABET.pdf`.
- Revisar la presentacion `VibraScope_1DoF/PPT VibraScope.pdf`.
- Leer `VibraScope.py` para entender la app actual.
- Leer `VibraScope_sensor/VibraScope_sensor.ino` para entender el formato serial.
- Identificar como se calcula y muestra hoy la distancia en la interfaz.
- Ejecutar la app actual y verificar que abre correctamente.
- Conectar el equipo fisico y comprobar lectura serial real.
- Registrar puertos, baudrate y flujo de uso real del laboratorio.
- Hacer una sesion de transferencia con la integrante nueva:
- explicar el objetivo educativo de VibraScope;
- explicar el sistema 1DoF fisico;
- explicar el flujo sensor -> ESP32 -> serial -> Python;
- explicar que partes del sistema son fijas y cuales se mueven.
- Crear un glosario basico con terminos clave:
- desplazamiento absoluto;
- desplazamiento relativo;
- cero de referencia;
- frecuencia;
- periodo;
- tasa de refresco;
- latencia.
- Tomar notas de dudas abiertas y riesgos tecnicos.

### Entregables

- documento corto de onboarding;
- diagrama simple del flujo de datos;
- lista de dudas y supuestos iniciales.

### Criterio de aceptacion

- la nueva integrante puede explicar con sus palabras como se obtiene hoy la medicion desde el sensor hasta Python.

## Semana 2 - Definicion funcional y decision tecnica

### Objetivo

Definir exactamente que hara la primera version del gemelo digital y con que stack se construira.

### Tareas

- Definir el objetivo minimo viable de la demo.
- Definir si el primer entregable sera:
- una app separada del sistema actual; o
- un modulo integrado a `VibraScope.py`.
- Recomendar una libreria 3D principal.
- Comparar brevemente `PyVista` y `VPython`.
- Tomar una decision documentada y justificarla.
- Definir el sistema de coordenadas del gemelo:
- cual sera el eje vertical;
- donde estara el origen;
- que signo corresponde a subir o bajar;
- como se mapearan mm reales a unidades 3D.
- Definir que partes del equipo seran:
- fijas;
- moviles;
- decorativas.
- Definir el rango esperado de movimiento.
- Definir como se hara el "set zero".
- Definir como se tratara una lectura invalida.
- Definir objetivos de refresco:
- tasa de lectura;
- tasa de animacion;
- latencia aceptable.
- Crear una especificacion corta de la version `v0.1`.

### Entregables

- decision tecnica de libreria;
- especificacion funcional `v0.1`;
- contrato de datos y reglas de calibracion.

### Criterio de aceptacion

- el equipo aprueba una descripcion clara de lo que si y lo que no incluira la primera version.

## Semana 3 - Prototipo 3D base del sistema

### Objetivo

Construir una primera escena 3D local que se mueva sin hardware, usando datos simulados.

### Tareas

- Crear carpeta de codigo para el prototipo del gemelo digital.
- Crear un entorno Python aislado para esta fase si hace falta.
- Instalar y probar la libreria 3D elegida.
- Definir si el modelo se construira:
- con primitivas geometricas simples; o
- importando una malla externa.
- Construir una version minima del equipo con:
- base;
- columnas;
- soporte superior;
- masa o bloque movil;
- representacion simple del resorte.
- Separar logicamente las piezas fijas de la pieza movil.
- Implementar una animacion de prueba con seno o triangulo.
- Verificar que la masa virtual sube y baja en el eje correcto.
- Ajustar camara inicial para una vista clara de laboratorio.
- Agregar etiquetas o texto simple si la libreria lo permite.
- Guardar capturas de pantalla de la escena.

### Entregables

- primer prototipo 3D ejecutable sin hardware;
- captura o video corto del movimiento simulado.

### Criterio de aceptacion

- el modelo 3D se mueve de manera visible, estable y comprensible con datos simulados.

## Semana 4 - Integracion con datos reales del prototipo fisico

### Objetivo

Conectar la escena 3D con la lectura serial real del sistema 1DoF.

### Tareas

- Reutilizar o adaptar la logica de lectura serial existente.
- Confirmar baudrate y formato real de las tramas.
- Crear una clase o modulo para lectura de datos.
- Crear un buffer pequeno para desacoplar lectura y render.
- Parsear correctamente valores `D:<valor>`.
- Manejar errores de conversion y lineas corruptas.
- Ignorar o marcar lecturas invalidas.
- Implementar conexion y desconexion limpias.
- Mover la masa 3D usando la distancia recibida.
- Implementar una primera funcion de conversion:
- distancia absoluta -> desplazamiento relativo.
- Anadir boton o atajo para fijar el cero.
- Mostrar en pantalla el valor actual de lectura.
- Probar con el sistema quieto.
- Probar con movimiento suave manual.
- Probar con oscilacion libre del sistema.

### Entregables

- demo 3D conectada a datos reales;
- lectura serial funcional dentro del modulo del gemelo digital.

### Criterio de aceptacion

- el modelo virtual responde a movimiento real del prototipo y no solo a datos simulados.

## Semana 5 - Calibracion, estabilidad y sincronizacion

### Objetivo

Reducir errores visuales y mejorar la fidelidad entre el sistema real y el modelo 3D.

### Tareas

- Medir si existe retardo perceptible entre sistema fisico y escena 3D.
- Registrar tasa real de llegada de datos.
- Registrar tasa real de refresco visual.
- Revisar si el movimiento se ve:
- brusco;
- retrasado;
- saturado;
- invertido;
- escalado incorrectamente.
- Implementar filtro simple si el ruido lo exige:
- media movil; o
- suavizado exponencial.
- Comparar visualmente sin filtro vs con filtro.
- Ajustar escala de desplazamiento para que la amplitud virtual sea coherente.
- Ajustar la posicion del cero para que el estado de equilibrio se vea bien.
- Limitar saltos grandes por lecturas erroneas.
- Documentar parametros de calibracion.
- Crear una rutina de arranque:
- conectar;
- estabilizar lectura;
- fijar cero;
- iniciar animacion.

### Entregables

- primera version calibrada;
- documento corto con parametros de ajuste.

### Criterio de aceptacion

- el movimiento del gemelo digital se percibe sincronizado y estable en una demo de laboratorio.

## Semana 6 - Interfaz util para demo y uso por terceros

### Objetivo

Convertir el prototipo tecnico en una herramienta demostrable y reutilizable.

### Tareas

- Disenar una interfaz minima limpia.
- Anadir selector de puerto COM.
- Anadir boton conectar/desconectar.
- Anadir boton set zero.
- Anadir indicador de estado del sensor.
- Anadir lectura numerica actual.
- Anadir aviso si no hay datos.
- Anadir boton para modo demo con senal simulada.
- Anadir opcion de reiniciar escena.
- Anadir configuracion basica persistente si es viable:
- ultimo puerto usado;
- escala;
- offset;
- velocidad de refresco.
- Mejorar camara, fondo e iluminacion de la escena.
- Verificar que la vista sea clara en laptop y proyector.
- Realizar pruebas con una persona que no desarrollo la app.

### Entregables

- version `v0.1` util para demostracion;
- lista de mejoras de usabilidad detectadas.

### Criterio de aceptacion

- otra persona puede abrir la app, conectarse y lanzar una demo siguiendo instrucciones simples.

## Semana 7 - Validacion, pruebas y documentacion tecnica

### Objetivo

Probar el sistema de manera ordenada y dejar evidencia de su funcionamiento.

### Tareas

- Disenar una bateria minima de pruebas.
- Probar con sistema en reposo.
- Probar con desplazamiento pequeno.
- Probar con desplazamiento medio.
- Probar con desplazamiento grande dentro del rango seguro.
- Probar multiples arranques y reconexiones.
- Probar desconexion accidental del puerto.
- Probar lectura invalida o perdida temporal.
- Medir comportamiento de la animacion bajo distintas condiciones.
- Registrar problemas reproducibles.
- Corregir fallos prioritarios.
- Preparar una guia de ejecucion paso a paso.
- Documentar dependencias e instalacion.
- Documentar la arquitectura del codigo.
- Documentar pendientes de la siguiente fase.

### Entregables

- reporte de pruebas;
- guia de instalacion y uso;
- lista priorizada de bugs y mejoras.

### Criterio de aceptacion

- existe evidencia clara de que el gemelo digital fue probado y no depende solo del conocimiento oral del desarrollador.

## Semana 8 - Cierre de fase, demo final y traspaso

### Objetivo

Cerrar la primera fase con una demo presentable, documentacion completa y continuidad asegurada.

### Tareas

- Preparar una demo final de laboratorio.
- Preparar un guion de presentacion de 3 a 5 minutos.
- Mostrar:
- sistema fisico;
- lectura en tiempo real;
- sincronizacion del modelo 3D;
- funciones de calibracion;
- limitaciones actuales.
- Grabar un video corto de evidencia.
- Ordenar la estructura del codigo.
- Limpiar archivos temporales o pruebas no usadas.
- Revisar nombres de archivos y carpetas.
- Consolidar el README final del modulo.
- Dejar backlog de fase 2:
- integracion con interfaz principal;
- importacion de modelo 3D mas fiel;
- extension a 2DoF;
- visualizacion conjunta 2D + 3D;
- registro de sesiones;
- analisis automatico.
- Hacer una sesion formal de traspaso con el equipo.

### Entregables

- demo final funcional;
- video corto de evidencia;
- documentacion consolidada;
- backlog de la siguiente fase.

### Criterio de aceptacion

- cualquier integrante del equipo puede entender donde quedo el proyecto, que funciona y cual es el siguiente paso.

## Riesgos tecnicos que deben vigilarse desde el inicio

- ruido o inestabilidad en la lectura del sensor;
- latencia alta entre sensor y escena 3D;
- mala alineacion entre el cero real y el cero visual;
- libreria 3D demasiado pesada para el hardware disponible;
- mezcla prematura entre refactor del sistema actual y construccion del gemelo digital;
- intentar demasiado realismo grafico antes de asegurar sincronizacion.

## Recomendaciones de gestion

- no integrar el gemelo digital en la app principal desde la semana 1;
- primero lograr un prototipo 3D separado que funcione bien;
- documentar decisiones pequenas conforme se toman;
- grabar pequenas demos semanales;
- validar cada semana con el hardware real, no solo con senales simuladas.

## Definicion de "hecho" para esta fase

Esta fase estara realmente terminada cuando exista una aplicacion reproducible que, al conectarse al sistema 1DoF fisico, muestre una masa virtual moviendose en tiempo real de forma entendible, estable y documentada.
