# Un nuevo enfoque para la evaluación de la marcha humana mediante visión computacional y dispositivos portátiles de medición inercial

Herramienta automatizada para el análisis de la marcha humana que combina sensores inerciales y visión por computadora para estimar el rango de movimiento, 
detectar fases del ciclo de la marcha y facilitar diagnósticos clínicos mediante una interfaz intuitiva.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Estructura de Carpetas](#estructura-de-carpetas)
- [Uso Visión Computacional](#uso-visión-computacional)
  - [Estatico](#estatico)
  - [TiempoReal](#tiemporeal)
  - [Video](#video)
- [Uso Sensores](#uso-sensores)
- [Uso Interfaz](#uso-interfaz)

## Descripción

Este proyecto propone una herramienta automatizada para el análisis preciso de la marcha humana, combinando sensores inerciales y visión computacional. 
El objetivo es superar las limitaciones de los métodos tradicionales (como el alto costo, la baja precisión y el tiempo requerido) mediante un sistema que integra tecnologías modernas y algoritmos de aprendizaje automático.

Los datos son recolectados mediante unidades de medición inercial (IMU) conectadas por Bluetooth, que estiman automáticamente parámetros clave como el rango de movimiento, velocidad, longitud del paso, ciclo de la marcha y cadencia. 
Simultáneamente, se procesan fotogramas de video para extraer las posiciones del tren inferior utilizando redes neuronales convolucionales. 

Esta información se emplea en una segunda estimación de arcos de movilidad, además de realizar predicciones sobre las fases de la marcha humana mediante modelos de machine learning entrenados con una base de datos de aproximadamente 
2,300 imágenes de adultos sanos de entre 20 y 25 años. El sistema identifica las 8 etapas del ciclo de la marcha con una precisión notable, alcanzando un F1 Score mínimo de 0.89 para la fase de "Oscilación Media" y un máximo de 0.96 para 
"Apoyo Medio", con una precisión global de 0.94. 

Ambas estimaciones se combinan para reducir la incertidumbre de las mediciones individuales. Finalmente, los resultados se presentan mediante una interfaz gráfica intuitiva que permite a profesionales de la salud acceder a herramientas de 
diagnóstico de bajo costo y alta precisión.

## Estructura de Carpetas

Explicación de la estructura de carpetas del repositorio:


- `/SensoresInerciales`: Codigos para usar los sensores IMU
  - `/WT9011DCL`:
    - `/Conexión`: Conexion via Bluetooth con 1 y 3 sensores.
    - `/Calibración`: Calibración de sensores WT9011DCL con comandos del fabricante.
    - `/Estimación`: Calculo de parametros de la marcha humana.
    - `/API`: Creación de una API con Conexion, Calibración y estimación de los sensores, y una interfaz.

- `/VisionComputacional`: Códigos con diferentes métodos de captura sobre visión computacional.
  - `/Estatico`: Estimación de arcos de movilidad en imágenes.
  - `/ModelosML`: Modelos preentrenados de ML junto con los scalers.
  - `/Pruebas`: Videos e imágenes que funcionan para probar los algoritmos.
  - `/TiempoReal`: Estimación de Arcos y predicción de fases de la marcha en tiempo real.
  - `/Video`: Estimación de arcos y predicción de fases de la marcha en un video pregrabado.

- `/Interfaz`: Proyecto en Unity para integrar y visualizar los resultados de los módulos de sensores y visión computacional.
  - `Assets/`: scripts en C# y recursos gráficos.
  - `Packages/`: dependencias gestionadas con el Unity Package Manager.
  - `ProjectSettings/`: configuración del proyecto (versión de Unity, compilación, gráficos).

## Uso Visión Computacional

Como se mencionó anteriormente, este apartado se divide en diferentes carpetas de las cuales nos enfocaremos en Estatico, TiempoReal y
Video. Empezaremos con el código de la API contenida en la primer carpeta;

### Estatico

En esta carpeta se encuentra el algoritmo `APIImagen.py`, en términos sencillos, la API recibe una imagen como entrada, detecta los puntos del cuerpo mediante mediapipe, estima los arcos de movimiento de puntos en cadera, rodilla y talón para dar como salida una imagen procesada que muestra los ángulos en colores intuitivos.

![Ejemplo: APIImagen](Imágenes/Estatico.png)

Para ejecutar la API es recomendable que se utilice una terminal; colóquese en el directorio de NEMI y ejecute el comando: `uvicorn VisionComputacional.Estatico.APIImagen:app`, esto le permitirá recibir imágenes y mandar la imagen codificada.
   
Esta API se utiliza también en el código: `VisionComputacional/TiempoReal/PruebasAPI.py`, el cual se describe a continuación.

### TiempoReal

En esta carpeta existen 3 códigos principales con diferentes métodos para hacer mediciones en tiempo real, todos se ven afectados en cierta medida por el gasto computacional, por lo que es importante tomar en cuenta la situación en que se utilizarán.

#### PruebasAPI.py

Comencemos con el código `PruebasAPI.py`, este es un ejemplo de como se podría utilizar la API en `VisionComputacional/Estatico/APIImagen.py`; Este algoritmo accede a la cámara principal de la computadora que se esté utilizando y manda las imágenes obtenidas para ser procesadas en la API y, al terminar el procesamiento, son mostradas en tiempo real. 

![Ejemplo: APIImagen en tiemporeal](Imágenes/APITiempoReal.PNG)

Como primer paso se tiene que ejecutar la API como se mostró en la subsección anterior y después ejecutar el código de python. Es importante destacar que la fluidez y el delay del video pueden verse afectada por la calidad de conexión, el tamaño de la captura de imágenes que se utilice, entre otras cosas.

#### AproximacionDeArcos.py

Este código funciona similar al anterior, accediendo a la cámara del usuario para obtener imágenes, procesarlas con ayuda de mediapipe y haciendo la estimación de los ángulos, su principal diferencia radica en que todo este proceso es local, por lo que disminuye el delay respecto a la API.

![Ejemplo: Aproximacion de arcos en tiempo real](Imágenes/ArcosTiempoReal.png)

Este código no requiere de otro para ser ejecutado. Una vez en uso la ventana abierta por opencv donde se muestran los resultados puede ser cerrada presionando la tecla `ESC`.

#### ArcosYEtapas

Este algoritmo se enfoca en agregar una nueva funcionalidad a los algoritmos anteriores, además de poder hacer la estimación de arcos en tiempo real, con ayuda de estos datos y los datos de posición de puntos importantes se utiliza un algoritmo de Machine Learning contenido en la carpeta `VisionComputacional/ModelosML` para poder clasificar la fase de la marcha en la que se encuentra la persona (CONTACTO INICIAL": "INITIAL CONTACT", "RESPUESTA A LA CARGA": "LOADING RESPONSE", "APOYO MEDIO": "MID-STANCE", "APOYO FINAL": "TERMINAL STANCE", "PRE OSCILACION": "PRE-SWING", "OSCILACION INICIAL": "INITIAL SWING", "OSCILACION MEDIA": "MID-SWING", "OSCILACION FINAL": "TERMINAL SWING").

![Ejemplo: Arcos y Etapas en tiempo real](Imágenes/EtapasTiempoReal.png)

Como el algoritmo anterior, no requiere de algo más para ser ejecutado y la ventana abierta por opencv se cierra con la misma tecla `ESC`.  Si se desea utilizar los nombres en español de las etapas es necesario cambiar el diccionario de `mapa_etiquetas` encontrado en el código.

### Video

Esta carpeta contiene algoritmos que funcionan con videos grabados anteriormente, surge con la finalidad de eliminar los posibles errores provocados por el gasto computacional de ejecutar los algoritmos en tiempo real.

#### ArcosYPredicciones.py

Este es un algoritmo que toma como entrada un video, en este caso está configurado para utilizar el video de `VisionComputacional/Pruebas/Gait.mp4`, aunque el código puede ser modificado para procesar otro. El proceso se basa en crear un nuevo video que muestra los ángulos estimados de miembros inferiores, así como las etapas predecidas por el algoritmo de machine learning de la carpeta `VisionComputacional/ModelosML`. Para poder tener una idea del proceso, también se muestra en la terminal o en donde se ejecute el código de python la cantidad de frames procesados y un porcentaje cada que este aumente un 5%. Como añadido a los anteriores algoritmos, este nos permite obtener al final obtener un archivo csv con la información del video, es decir, los arcos de movilidad, tiempos y la predicción de la etapa de la marcha.

![Ejemplo: Arcos y Predicciones en Video](Imágenes/ArcosYPredicciones.png)

Este código no requiere de ejecutar algo más, simplemente con tener una entrada de video junto con los algoritmos preentrenados del scaler y el modelo de ML funciona. Se puede modificar el nombre del video de salida y el archivo csv en el algoritmo así como el destino de estos, si no se modifica el algoritmo guardará tanto el video como el csv en la carpeta `VisionComputacional/Pruebas`.

#### APIVideo.py

Esta API cuenta con distintos apartados para hacer funcionar correctamente todo lo que se mencionó en el algoritmo anterior; El primer apartado es en el que se puede subir y procesar el video, tiene como salida tanto el csv como el video con estimaciones de arcos y la predicción de las etapas de la marcha. Para descargar estos dos también se guarda el número serial generado en carpetas temporales por ambos, así entonces, con el segundo y tercer apartado se pueden extraer para poder guardarse en la computadora. Finalmente existe otro apartado para eliminar los archivos temporales y poder empezar desde cero los procesos.

![Ejemplo: API para videos](Imágenes/APIVideo.png)

Esta API se puede ejecutar utilizando una terminal con el comando `uvicorn VisionComputacional.Video.APIVideo:app`, esto le permitirá subir videos, descargar las salidas y reiniciar el programa en interfaces como Swagger o utilizando un programa como el que se mostrará a continuación.

#### PruebaAPI.py

En este algoritmo se utiliza la API mencionada anteriormente, solamente requiere el archivo de entrada para descargar automáticamente las salidas (el video procesado y el archivo csv), si no se configura un nombre o ruta de destino diferente las salidas se encontrarán en la carpeta `VisionComputacional/Pruebas`, como adición en la terminal se mostrará el progreso que lleva el analisis del video por lo que puede revisarse en cualquier momento.

![Ejemplo: Prueba de la API para videos](Imágenes/PruebaAPIVideo.png)

Es claro que para utilizar el código se debe ejecutar el archivo `APIVideo.py` en una terminal con el comando `uvicorn VisionComputacional.Video.APIVideo:app`, después, de ser necesario, se debe cambiar el nombre del archivo de entrada para posteriormente ejecutar el algoritmo y así poder observar las salidas y el progreso.

## Uso Sensores
Como se mencionó anteriormente, este apartado se divide en diferentes carpetas que contienen los códigos necesarios para establecer la conexión con los sensores WT9011DCL, calibrarlos, estimar parámetros de la marcha y desplegar los resultados en una interfaz. A continuación se describe el contenido de cada una de ellas.

### Conexión
En esta carpeta se encuentran dos códigos principales:

- 1sensor.py
Este código establece la conexión vía Bluetooth con un solo sensor WT9011DCL. Permite recibir y visualizar datos en crudo (acelerómetro, giroscopio, magnetómetro) para comprobar que el sensor funciona correctamente.

- 3sensores.py
Similar al anterior, pero pensado para la conexión simultánea de tres sensores WT9011DCL. Los datos recibidos se diferencian por cada sensor y pueden ser usados posteriormente en la estimación de parámetros de la marcha.

Estos códigos se ejecutan directamente en Python desde la terminal.

### Calibración 
Esta carpeta contiene los archivos necesarios para la calibración de los sensores.

- calibracion.py
Es un script que ejecuta automáticamente los comandos de calibración sobre el sensor conectado y permite obtener datos corregidos. Incluye la calibración de acelerómetro, giroscopio y magnetómetro.

- comandos.txt
Contiene únicamente los comandos en hexadecimal necesarios para realizar manualmente la calibración de los sensores (ejemplo: calibración del giroscopio, restauración de valores de fábrica, etc.).

### Estimación
En esta carpeta se encuentra el archivo:

- estimacion.py
Este código procesa los datos recibidos de los sensores y realiza los cálculos necesarios para obtener los parámetros de la marcha humana. Entre ellos:
- Detección de pasos
- Cálculo de cadencia
- Velocidad de marcha
- Longitud de paso

### API
El archivo puede ejecutarse directamente y mostrará los resultados en consola o los exportará según la configuración.
Finalmente, esta carpeta concentra los códigos que integran todo lo anterior en un servicio accesible:

- API.py
Implementado con FastAPI, permite recibir datos de los sensores, aplicar la calibración y realizar la estimación de parámetros de la marcha. El servidor puede levantarse desde la terminal:
uvicorn WT9011DCL.API.API:app
Esto habilita endpoints para consultar los datos procesados desde un navegador o cliente HTTP.

- interfaz.py
Es una interfaz gráfica que se conecta con la API para mostrar de forma visual los datos de los sensores, las estimaciones de la marcha y las gráficas en tiempo real.

## Uso Interfaz

El apartado de Interfaz contiene el proyecto de Unity que permite la visualización e interacción con los datos obtenidos de sensores y de visión computacional. 

Estructura del proyecto

Dentro de la carpeta `Interfaz/` se encuentran las carpetas principales de cualquier proyecto Unity:

`Assets/`: contiene los scripts en C# y los recursos del proyecto.

`Packages/`: define las dependencias de Unity utilizadas.

`ProjectSettings/`: incluye la configuración del proyecto, como versión de Unity, ajustes de compilación y parámetros gráficos.

Para abrir el proyecto, basta con abrir Unity Hub, seleccionar la opción Open, navegar hasta la carpeta `Interfaz/` y elegirla como proyecto.

### Pantalla principal
Al ejecutar la escena principal del proyecto en Unity, se despliega un menú inicial que contiene los apartados:

#### Visión artificial

Grabar en tiempo real: abre el módulo para capturar y procesar video en directo desde la cámara del equipo, haciendo uso de los algoritmos descritos en `VisionComputacional/`.

Subir video: permite cargar un archivo de video previamente grabado para ser procesado en la API de visión artificial.

#### Sensores

Grabar en tiempo real: accede al módulo que recibe los datos enviados por los sensores inerciales conectados.

Simulación: abre la escena de simulación en Unity, donde se visualiza en tiempo real un esqueleto animado controlado con los datos adquiridos.

### Ejecución

1. Abre el proyecto en Unity Hub seleccionando la carpeta `Interfaz/`.

2. En el editor, abre la escena principal (marcha).

3. Presiona Play para iniciar la ejecución de la interfaz.

4. Selecciona el apartado que desees utilizar: Visión artificial o Sensores.
