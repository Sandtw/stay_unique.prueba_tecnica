
*** Settings ***
Library           SeleniumLibrary
Library           OperatingSystem
Library           Collections
Library           resources/utils.py

*** Variables ***
${url}    https://www.airbnb.com.pe
${browser}    Chrome

${input_busqueda_destino}    //input[@id = "bigsearch-query-location-input"]
${button_busqueda_destino}    //button[@data-testid = "structured-search-input-search-button"]
${button_busqueda_idioma_moneda}    //button[@aria-label = "Elige un idioma y una moneda"]
${button_busqueda_moneda}    //button[@id = "tab--language_region_and_currency--1"]
# ${button_moneda}     //button/div[text() = "EUR – €"]
${page_result_busqueda_destino}    //span[@data-testid = "stays-page-heading"]
${base_paginacion}    //nav[@aria-label='Paginación de los resultados de búsqueda']/div
${base_propiedades_pagina}    //div[@id='site-content']/div/div[2]/div/div/div/div/div


*** Keywords ***

Open Airbnb
    [Arguments]    ${currency}    ${city}    ${country}
    ${locales}    Create List

    ${place}    Set Variable    ${city}, ${country}
    Open Browser    ${url}/?currency=${currency}    ${browser}    options=add_argument("--headless") 
    Maximize Browser Window


    Wait Until Element Is Visible    ${input_busqueda_destino}    timeout=10
    Input Text    ${input_busqueda_destino}    ${place}
    Wait Until Element Is Visible    ${button_busqueda_destino}
    Click Element    ${button_busqueda_destino}
    
    Wait Until Element Is Visible    ${page_result_busqueda_destino}    timeout=10
    Wait Until Element Is Visible    ${base_paginacion}    timeout=10
    
    ${count_paginacion}    Get Element Count    ${base_paginacion}/*
    ${max_paginacion}    Get Text    ${base_paginacion}/*[${count_paginacion}-1]

    FOR    ${index}    IN RANGE    1    ${max_paginacion} + 1
        IF    ${index} != 1
            Log To Console    Pasando a la pagina ${index}
            ${xpath_nro_pagina}    Set Variable    ${base_paginacion}/a[text()='${index}']
            ${href_nro_pagina}    Get Element Attribute    ${xpath_nro_pagina}    href
            Click Element    ${xpath_nro_pagina}
            Sleep    2s
            Wait Until Element Is Visible    ${page_result_busqueda_destino}    timeout=10
        END

        ${count_paginacion}    Get Element Count    //div[@data-testid="card-container"]
        FOR    ${index_propiedad}    IN RANGE    1    ${count_paginacion} + 1
            ${card_propiedad}    Set Variable    (//div[@data-testid="card-container"])[${index_propiedad}]
            Log To Console    -> ${index}:${card_propiedad}
            ${id_propiedad}     ${nombre_propiedad}    ${precio_noche}    ${texto_puntuacion}    ${url_propiedad}    Extraction Property    ${card_propiedad}    ${currency} 
            ${local}    Create List    ${id_propiedad}    ${nombre_propiedad}    ${precio_noche}    ${texto_puntuacion}   ${city}    ${country}    airbnb    ${url_propiedad} 
            Append To List    ${locales}    ${local}        
        END

    END
    
    Export To CSV    ${locales}
    

Extraction Property
    [Arguments]    ${base_ind_paginacion}    ${currency}     # div[@aria-label='Cargando']/div/div[n]
    Wait Until Element Is Visible    ${base_ind_paginacion}

    ${id_titulo_propiedad}    Get Element Attribute    ${base_ind_paginacion}/div/div[2]/div[1]   id
    ${id_propiedad}    Evaluate    '${id_titulo_propiedad}'.split('_')[1]
    ${nombre_propiedad}    Get Text    ${base_ind_paginacion}/div/div[2]/div[1]         #//div[@id='${id_titulo_propiedad}']

    ${url_propiedad}    Get Element Attribute    ${base_ind_paginacion}/a    href
    ${url_propiedad}    Set Variable    ${url_propiedad}&currency=${currency}
    ${bool_puntuacion}    Run Keyword And Return Status    Wait Until Element Is Visible    ${base_ind_paginacion}/div/div[2]/div[last()]/span/span[last()]    timeout=2.5
    IF    ${bool_puntuacion}
        ${texto_puntuacion}    Get Text    ${base_ind_paginacion}/div/div[2]/div[last()]/span/span[last()]
    ELSE
        ${texto_puntuacion}    Evaluate    None
    END
    ${precio_noche}    Get Text    ${base_ind_paginacion}/div/div[2]/div[@data-testid='price-availability-row']//span/div/span[last()-1]

    RETURN    ${id_propiedad}     ${nombre_propiedad}    ${precio_noche}    ${texto_puntuacion}    ${url_propiedad}
    
*** Test Cases ***
Proceso Airbnb
    Open Airbnb    EUR    Barcelona    España

