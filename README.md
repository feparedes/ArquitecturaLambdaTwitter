Este proyecto se ha realizado en la asignatura Análisis de Datos en Sistemas
de información. Se ha realizado junto con mi compañero Francisco Mohedano.

El proyecto consiste en realizar una arquitectura Lambda la cual ingeste
datos a través de la librería Tweepy que ofrece una API para peticiones
a Twitter.

Esta arquitectura lambda consta de 4 capas:

* Data Ingestor: es la capa encargada de ingestar los datos de Twitter y
procesarlos mediante Kafka y MongoDB como DataLake.

* Speed Layer: es la capa de velocidad, trata los datos en tiempo real
a través de Spark Streaming consumiendo los datos del servidor de Kafka.
El tratamiento que se le hace a los datos es un filtrado para quedarnos
con los hashtags y estructurarlo en formato JSON.

* Batch Layer: es la capa offline o batch, en ella tratamos los datos (tweets)
cada 100 segundos. Accedemos al DataLake y procesamos la información 
obteniendo los hashtags.

* Service Layer: es la capa de servicio, en ella ejecutamos mediante Flask
y Javascript distintas gráficas para visualizar los datos procesados.

Los archivos que componen este proyecto son

* main.py: clase principal donde se llama a las clases 
