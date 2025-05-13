# Un nuevo enfoque para la evaluación de la marcha humana mediante visión computacional y dispositivos portátiles de medición inercial

Herramienta automatizada para el análisis de la marcha humana que combina sensores inerciales y visión por computadora para estimar el rango de movimiento, 
detectar fases del ciclo de la marcha y facilitar diagnósticos clínicos mediante una interfaz intuitiva.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Estructura de Carpetas](#estructura-de-carpetas)

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


- `/SensoresInerciales`: Pendiente.

- `/VisionComputacional`: Códigos con diferentes metódos de captura sobre visión computacional.
  - `/Estatico`: Estimación de arcos de movilidad en imágenes.
  - `/ModelosML`: Modelos pre-entrenados de ML junto con los scalers.
  - `/Pruebas`: Videos e imágenes que funcionan para probar los algoritmos.
  - `/TiempoReal`: Estimación de Arcos y predicción de fases de la marcha en tiempo real.
  - `/Video`: Estimación de arcos y predicción de fases de la marcha en un video pre-grabado.

- `/Interfaz`: Pendiente.

## Uso



