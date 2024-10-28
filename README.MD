# Prueba técnica - Data Engineer JR

## Configuraciones previas
Empezaré implementando mi ambiente llamado `env` más la definición de los requerimientos.

```cmd
py -3.12 -m venv env
env\Scripts\activate

pip install selenium numpy pandas requests robotframework robotframework-seleniumlibrary

pip install google-api-python-client google-cloud-storage google-cloud-bigquery google-cloud-bigquery-storage google-cloud-core google-auth google-auth-oauthlib

pip install mitmproxy

pip install pymysql sqlalchemy python-decouple

pip install beautifulsoup4

pip install lxml
```


## Ejercicio 1: Scrapping sobre una página de propiedades vacaciones (Booking y Airbnb)

Flujo del programa:
- Entrada: Lugar, Cantidad de propiedades, Año
- Extracción: Nombre, Direccion, Precio x noche, Puntuacion Reseñas, NHabitaciones
- Salida: Archivo csv


Para este ejercicio utilizaré la plataforma de airbnb y los siguientes conceptos/tecnologías.

- Selenium: Me permitirá manejar contenido dinámico (javacript y frameworks), así como la paginación de URLs dinámicas.
- xpath: Fácil de obtener por el DOM de la plataforma
- Chromedriver: Driver que me permitirá interactuar con la plataform y extraer los datos.
- Python:
    - Pandas: Me permitirá manipular los datos extraídos y guardarlos en un csv

Plus:
    - Haré una muestra de como se puede utilizar RobotFramework, da mayor facilidad en interacción con la plataforma utilizando selenium internamente

