from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import requests
#from bs4 import BeautifulSoup as bs

from resources.utils import export_to_csv

input_busqueda_destino:str = "//input[@id = 'bigsearch-query-location-input']"
button_busqueda_destino:str = "//button[@data-testid = 'structured-search-input-search-button']"
page_result_busqueda_destino:str = "//span[@data-testid = 'stays-page-heading']"
base_paginacion:str = "//nav[@aria-label='Paginación de los resultados de búsqueda']/div"
properties_paginacion:str = "//div[@data-testid='card-container']"
url_aibnb:str = "https://www.airbnb.com.pe"

def scrap_airbnb(currency:str, city:str, country:str):
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        place = f"{city}, {country}"
        driver.get(f"{url_aibnb}/?currency={currency}")

        # Input de busqueda de destino
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, input_busqueda_destino)))
        driver.find_element(By.XPATH, input_busqueda_destino).send_keys(place)
        # Boton de busqueda de destino
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, button_busqueda_destino)))
        driver.find_element(By.XPATH, button_busqueda_destino).click()

        # Resultado de busqueda de destino
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, page_result_busqueda_destino)))
        list_properties = extraction_properties(driver, currency, city, country)
        export_to_csv(list_properties)

    except Exception as e:
        print(f"Error en la ejecución: {e}")
    
    finally:
        if driver:
            driver.quit()

def extraction_properties(driver:any, currency:str, city:str, country:str):
    list_properties:list = []

    # Manejo de paginaciones
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, base_paginacion)))
    count_nav_paginacion = len(driver.find_elements(By.XPATH, f"{base_paginacion}/*"))
    max_paginacion = driver.find_element(By.XPATH, f"{base_paginacion}/*[{count_nav_paginacion}-1]").text

    for page_i in range(1, int(max_paginacion) + 1):
        if page_i != 1:
            print(f"Pasando a la pagina {page_i}")
            # Manejo del click en cada paginacion
            xpath_nro_pagina = f"{base_paginacion}/a[text()='{page_i}']"
            driver.find_element(By.XPATH, xpath_nro_pagina).click()
            # Esperamos que la paginacion se cargue correctamente
            time.sleep(2)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, page_result_busqueda_destino)))

        count_properties = len(driver.find_elements(By.XPATH, properties_paginacion))
        for propiedad_i in range(1, count_properties + 1):
            card_propiedad = f"({properties_paginacion})[{propiedad_i}]"
            id_propiedad, nombre_propiedad, precio_noche, puntuacion, nro_reseñas, tipo_propiedad, url_propiedad = extraction_property(driver, card_propiedad, currency)
            property = [id_propiedad, nombre_propiedad, precio_noche, puntuacion, nro_reseñas, city, country, tipo_propiedad, url_propiedad]
            print(f"-> {property}")
            list_properties.append(property)

    return list_properties

def extraction_property(driver:any, base_ind_paginacion:str, currency:str):
    # Esperamos que la propiedad se cargue correctamente
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, base_ind_paginacion)))

    # Captura de datos del elemento card de la propiedad
    id_titulo_propiedad = driver.find_element(By.XPATH, f"{base_ind_paginacion}/div/div[2]/div[1]").get_attribute("id")
    id_propiedad = id_titulo_propiedad.split('_')[1]
    nombre_propiedad = driver.find_element(By.XPATH, f"{base_ind_paginacion}/div/div[2]/div[1]").text
    text_propiedad = re.search(r"(habitación|apartamento|casa|suite|alojamiento)", nombre_propiedad, re.IGNORECASE)
    tipo_propiedad = text_propiedad.group(1) if text_propiedad else "No reconocido"

    url_propiedad = driver.find_element(By.XPATH, f"{base_ind_paginacion}/a").get_attribute("href")
    url_propiedad = f"{url_propiedad}&currency={currency}"

    #? A veces la puntuación se encuentra como (novedad, numero, vacío)
    try:
        WebDriverWait(driver, 2.5).until(
            EC.presence_of_element_located((By.XPATH, f"{base_ind_paginacion}/div/div[2]/div[last()]/span/span[last()]"))
        )
        texto_puntuacion = driver.find_element(By.XPATH, f"{base_ind_paginacion}/div/div[2]/div[last()]/span/span[last()]").text
        search_puntuacion = re.search(r"(.*)\((\d+)\)", texto_puntuacion)
        if search_puntuacion:
            puntuacion = search_puntuacion.group(1).strip()
            nro_reseñas = search_puntuacion.group(2)
        else:
            puntuacion = 0
            nro_reseñas = 0
    except:
        puntuacion = -1
        nro_reseñas = 0

    text_noche = driver.find_element(By.XPATH, f"{base_ind_paginacion}/div/div[2]/div[@data-testid='price-availability-row']//span/div/span[last()-1]").text
    precio_noche = re.sub(r"[^0-9\.,]", "", text_noche)

    return id_propiedad, nombre_propiedad, float(precio_noche), float(puntuacion), int(nro_reseñas), tipo_propiedad, url_propiedad

