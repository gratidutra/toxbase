# import chromedriver_autoinstaller
import time
import xml.etree.ElementTree as ET
import logging


import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as Options_f
from selenium.webdriver.chrome.options import Options

import os

logging.basicConfig(level=logging.DEBUG)


def pubchem_extractor(cas_numbers):

    if isinstance(cas_numbers, str):
        cas_numbers = [cas_numbers]

    pubchem_data = pd.DataFrame()

    # Definir as opções do Firefox
    options = Options()
    options.add_argument("--headless")  # Rodar sem interface gráfica
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    for cas_number in cas_numbers:
        # Initialize the WebDriver with the options
        driver = webdriver.Remote(
            command_executor="http://selenoid:4444/wd/hub", options=options
        )
       try:
            # Inicializar o navegador

            # Acessar a página do PubChem
            url = "https://pubchem.ncbi.nlm.nih.gov/"
            driver.get(url)

            time.sleep(5)

            # Inserir o número CAS na barra de pesquisa
            search = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div[2]/form/div/div[1]/input",
            )
            search.send_keys(cas_number)
            search.send_keys(Keys.RETURN)

             # Aguardar até que o elemento clicável esteja disponível
            WebDriverWait(driver, 17).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div/main/div[2]/div[1]/div/div[2]/div/div[1]/div[2]/div[1]/a/span/span",
                    )
                )
            ).click()

            # Esperar para carregar os detalhes
            time.sleep(10)

             # Função auxiliar para buscar um elemento de forma segura
            def get_text_or_default(xpath, default="Não encontrado"):
                elements = driver.find_elements(By.XPATH, xpath)
                return elements[0].text if elements else default

            # Extração dos dados
            cid = get_text_or_default('//div[text()="PubChem CID"]/following-sibling::div')
            molecular_formula = get_text_or_default('//div[text()="Molecular Formula"]/following-sibling::div')
            synonyms = get_text_or_default('//div[text()="Synonyms"]/following-sibling::div')
            molecular_weight = get_text_or_default('//div[text()="Molecular Weight"]/following-sibling::div')
            dates = get_text_or_default('//div[text()="Dates"]/following-sibling::div')
            description = get_text_or_default('//div[text()="Description"]/following-sibling::div')


            # Criar um dicionário com os dados extraídos
            dict_data = {
                "CAS Number": [cas_number],
                "CID": [cid],
                "Fórmula Molecular": [molecular_formula],
                "Sinônimos": [synonyms],
                "Peso Molecular": [molecular_weight],
                "Datas": [dates],
                "Descrição": [description]
            }

            # Criar um DataFrame e adicionar ao DataFrame final
            data = pd.DataFrame(dict_data)
            pubchem_data = pd.concat([pubchem_data, data], ignore_index=True)

        except Exception as e:
            print(f"Erro ao processar o CAS Number {cas_number}: {e}")
        finally:
            # Fechar o navegador
            driver.quit()

    return pubchem_data


def echa_extractor(cas_numbers):
    # Certificar-se de que cas_numbers é uma lista
    if isinstance(cas_numbers, str):
        cas_numbers = [cas_numbers]

    # Instalar e configurar o driver automaticamente
    echa_data = pd.DataFrame()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    for cas_number in cas_numbers:
        try:
            # Initialize the WebDriver with the options
            driver = webdriver.Remote(
                command_executor="http://selenoid:4444/wd/hub", options=options
            )
            print(f"WebDriver inicializado para o CAS Number: {cas_number}")

            # Acessar a página
            driver.get("https://echa.europa.eu/pt/information-on-chemicals")
            print("Página acessada com sucesso")

            # Configurar WebDriverWait
            wait = WebDriverWait(driver, 15)
            actions = ActionChains(driver)

            # Aceitar cookies
            cookie_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="cookie-consent-banner"]/div/div/div[2]/a[1]')
                )
            )
            cookie_button.click()
            print('Cookies aceitos')
            time.sleep(2)

            # Selecionar checkbox
            checkbox = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="_disssimplesearchhomepage_WAR_disssearchportlet_fm"]/div[2]/label/span',
                    )
                )
            )
            actions.move_to_element(checkbox).click().perform()
            print("Checkbox selecionado")
            time.sleep(2)

            # Inserir o número CAS na barra de pesquisa
            search = driver.find_element(By.XPATH, '//*[@id="autocompleteKeywordInput"]')
            search.send_keys(cas_number)
            search.send_keys(Keys.RETURN)
            print("Número CAS inserido e pesquisa realizada")
            time.sleep(2)

            # Aguardar até que o elemento esteja visível e clicável
            element = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="_disssimplesearch_WAR_disssearchportlet_rmlSearchResultVOsSearchContainerSearchContainer"]/table/tbody/tr[1]/td[1]/a',
                    )
                )
            )
            element.click()
            print("Elemento clicado")
            time.sleep(2)

              # Função auxiliar para buscar um elemento de forma segura
            def get_text_or_default(xpath, default="Não encontrado"):
                elements = driver.find_elements(By.XPATH, xpath)
                return elements[0].text if elements else default

            # Extração de informações específicas
            ec = get_text_or_default('//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[1]/div/div/div/p[1]')
            cas = get_text_or_default('//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[1]/div/div/div/p[3]')
            molecular_formula = get_text_or_default('//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[1]/div/div/div/p[3]')
            haz_classification_labelling = get_text_or_default('//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[2]/div/div/div/p')
            about_1 = get_text_or_default('//*[@id="aboutSubstanceParagraphWrapper"]/p[1]')
            about_2 = get_text_or_default('//*[@id="aboutSubstanceParagraphWrapper"]/p[2]')
            consumer_user = get_text_or_default('//*[@id="aboutSubstanceParagraphWrapper"]/p[3]')

            # Criar um dicionário com os dados extraídos
            dict_data = {
                "CAS Number": [cas],
                "EC": [ec],
                "Fórmula Molecular": [molecular_formula],
                "HAZ Classificação": [haz_classification_labelling],
                "Sobre 1": [about_1],
                "Sobre 2": [about_2],
                "Uso Consumidor": [consumer_user],
            }

            data = pd.DataFrame(dict_data)
            echa_data = pd.concat([echa_data, data], ignore_index=True)
            print(f"Dados extraídos para o CAS Number: {cas_number}")

        except Exception as e:
            print(f"Erro ao processar o CAS Number {cas_number}: {e}")
        finally:
            # Fechar o navegador
            driver.quit()
            print("WebDriver fechado")

    return echa_data


def extract_data(cas_numbers, databases):
    """
    Recebe os CAS Numbers e os bancos de dados selecionados,
    e chama as funções corretas para extração, retornando DataFrames.
    """
    cas_list = [cas.strip() for cas in cas_numbers.split(",") if cas.strip()]

    if not cas_list:
        return {}

    results = {}

    for cas in cas_list:
        results[cas] = {}

        if "PubChem" in databases:
            results[cas]["PubChem"] = pubchem_extractor(cas)

        if "ECHA" in databases:
            results[cas]["ECHA"] = echa_extractor(cas)

    return results
