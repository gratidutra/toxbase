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
from flask import jsonify

import os

import json
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as Options_f
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def pubchem_extractor(cas_numbers):
    if isinstance(cas_numbers, str):
        cas_numbers = [cas_numbers]

    extracted_data = []  # Lista para armazenar os dados extraídos

    # Definir as opções do Firefox
    options = Options_f()
    options.add_argument("--headless")  # Rodar sem interface gráfica
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    for cas_number in cas_numbers:
        driver = webdriver.Remote(
            command_executor="http://selenoid:4444/wd/hub", options=options
        )
        try:
            # Acessar a página do PubChem
            url = "https://pubchem.ncbi.nlm.nih.gov/"
            driver.get(url)
            time.sleep(3)

            # Inserir o número CAS na barra de pesquisa
            search = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div[2]/form/div/div[1]/input"
            )
            search.send_keys(cas_number)
            search.send_keys(Keys.RETURN)

            # Aguardar até que o elemento clicável esteja disponível
            WebDriverWait(driver, 45).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div/main/div[2]/div[2]/div[3]/div/div/div/div[2]/ul/li/div/div/div[1]/div[2]/div[1]/a/span/span"
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
            extracted_data.append({
                "CAS Number": cas_number,
                "CID": get_text_or_default('//div[text()="PubChem CID"]/following-sibling::div'),
                "Fórmula Molecular": get_text_or_default('//div[text()="Molecular Formula"]/following-sibling::div'),
                "Sinônimos": get_text_or_default('//div[text()="Synonyms"]/following-sibling::div'),
                "Peso Molecular": get_text_or_default('//div[text()="Molecular Weight"]/following-sibling::div'),
                "Datas": get_text_or_default('//div[text()="Dates"]/following-sibling::div'),
                "Descrição": get_text_or_default('//div[text()="Description"]/following-sibling::div')
            })

        except Exception as e:
            print(f"Erro ao processar o CAS Number {cas_number}: {e}")
        finally:
            driver.quit()

    return extracted_data

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
            time.sleep(2)

            # Inserir o número CAS na barra de pesquisa
            search = driver.find_element(By.XPATH, '//*[@id="autocompleteKeywordInput"]')
            search.send_keys(cas_number)
            search.send_keys(Keys.RETURN)
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
            time.sleep(3)

              # Verificar se o botão "Registered" está habilitado
            try:
                registered_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="_disssubsinfo_WAR_disssubsinfoportlet_dataset-reg-button"]/span')))
                if not registered_button.is_enabled():
                    print(f"Botão 'Registered' desabilitado para o CAS {cas_number}.")
                    continue  # Cenário 3: Botão desabilitado
            except:
                print(f"Botão 'Registered' não encontrado para o CAS {cas_number}.")
                continue

            # Se o botão "Registered" está habilitado, verificar se abre uma nova aba
            registered_button.click()
            time.sleep(2)

            # Verificar se uma nova aba foi aberta
            tabs = driver.window_handles
            if len(tabs) > 1:
                # Cenário 2: Nova aba aberta
                driver.switch_to.window(tabs[1])

                registered_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_dissregisteredsubstances_WAR_dissregsubsportlet_disregOutputitemVOsSearchContainerSearchContainer"]/table/tbody/tr[1]/td[9]/a')))
                registered_button.click()
              
                    # Espera um pouco para a nova aba carregar (ou use WebDriverWait)
                time.sleep(2)
                    
                    # Alterna para a nova aba
                driver.switch_to.window(driver.window_handles[1])
                    
                # Capturar a URL da nova aba
                url_new_tab = driver.current_url
                print(f"URL da nova aba para o CAS {cas_number}: {url_new_tab}")

                if len(driver.window_handles) > 1:
                    for handle in driver.window_handles[:-1]:
                        driver.switch_to.window(handle)
                        driver.close()
                
                    # Alterna para a aba mais recente
                    driver.switch_to.window(driver.window_handles[0])

            else:
                # Cenário 1: Não abre nova aba
                url_current_page = driver.current_url
                print(f"URL da página de interesse para o CAS {cas_number}: {url_current_page}")


            nav_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainNav7"]/a')))
            nav_button.click()

            element = driver.find_element(By.XPATH, '//*[@id="SubNav7_1"]/a')
            driver.execute_script("arguments[0].click();", element)
    
            # XPath base
            xpath_base = '//*[@id="MainContent"]'
            
            # Encontrar elementos dentro da hierarquia do XPath base
            main_div = driver.find_element(By.XPATH, f"{xpath_base}//*")
                        
            # Encontra todas as seções <h3> dentro de main-content
            secoes_h3 = main_div.find_elements(By.TAG_NAME, "h3")
        
            # Lista para armazenar os dados organizados
            todas_secoes = []
        
            for secao_h3 in secoes_h3:
                secao_nome = secao_h3.text.strip()
                secao_dict = {"seção": secao_nome, "subseções": []}
        
                # Pegar todos os <h4> que aparecem depois desse <h3> e antes do próximo <h3>
                subsecoes_h4 = secao_h3.find_elements(By.XPATH, "./following-sibling::h4")
        
                for subsecao_h4 in subsecoes_h4:
                    subsecao_nome = subsecao_h4.text.strip()
                    subsecao_dict = {"subseção": subsecao_nome, "dados": {}}
        
                    # Pegar todos os <h5> que aparecem depois desse <h4> e antes do próximo <h4> ou <h3>
                    subsecoes_h5 = subsecao_h4.find_elements(By.XPATH, "./following-sibling::h5")
        
                    for subsecao_h5 in subsecoes_h5:
                        subsubsecao_nome = subsecao_h5.text.strip()
                        dados_dict = {"dados_textuais": []}
        
                        # Encontrar <dt> e <dd> dentro da mesma subseção
                        elementos_dt = subsecao_h5.find_elements(By.XPATH, "./following-sibling::dl/dt")
                        elementos_dd = subsecao_h5.find_elements(By.XPATH, "./following-sibling::dl/dd")
        
                        for dt, dd in zip(elementos_dt, elementos_dd):
                            chave = dt.text.strip()
                            valor = dd.text.strip()
                            dados_dict[chave] = valor
        
                        # Capturar parágrafos <p> dentro da subseção
                        paragrafos = subsecao_h5.find_elements(By.XPATH, "./following-sibling::p")
                        for p in paragrafos:
                            texto_p = p.text.strip()
                            if texto_p:  # Evita adicionar parágrafos vazios
                                dados_dict["dados_textuais"].append(texto_p)
        
                        subsecao_dict["dados"][subsubsecao_nome] = dados_dict
        
                    secao_dict["subseções"].append(subsecao_dict)
        
                todas_secoes.append(secao_dict)
        
            # Converte para JSON formatado
            json_resultado = json.dumps(todas_secoes, indent=4, ensure_ascii=False)
        
            print(json_resultado)

        except Exception as e:
            print(f"Erro ao processar o CAS Number {cas_number}: {e}")
        finally:
            # Fechar o navegador
            driver.quit()

    return json_resultado

def extract_data(cas_numbers, databases):
    """
    Recebe os CAS Numbers e os bancos de dados selecionados,
    e chama as funções corretas para extração, retornando um dicionário.
    """
    cas_list = [cas.strip() for cas in cas_numbers.split(",") if cas.strip()]

    if not cas_list:
        return {"error": "Nenhum CAS Number válido fornecido."}

    results = {}

    for cas in cas_list:
        results[cas] = {}

        if "PubChem" in databases:
            results[cas]["PubChem"] = pubchem_extractor(cas)  # Retorna um dicionário

        if "ECHA" in databases:
            results[cas]["ECHA"] = echa_extractor(cas)  # Retorna um dicionário

    return results