#import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import os, sys
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

def fetch_toxin_xml(toxin_id):
    """
    Fetch XML data for a given toxin ID from the T3DB database.
    """
    
    base_url = f"http://www.t3db.ca/toxins/{toxin_id}.xml"
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Ensure the request was successful
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching toxin XML for ID {toxin_id}: {e}")
        return None

def parse_xml_to_table(xml_content):
    """
    Parse XML content into a pandas DataFrame with one row of data.
    """
    try:
        root = ET.fromstring(xml_content)
        data = {}

        # Extract key-value pairs from the XML structure
        for element in root:
            data[element.tag] = element.text

        # Convert the dictionary to a DataFrame
        return pd.DataFrame([data])
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on parse failure

def t3db_extractor(cas_numbers, delay=1):
    """
    Process a list of toxin IDs and fetch their data with a delay between requests.
    
    Args:
        cas_number (list): List of toxin IDs to process.
        delay (int or float): Time in seconds to wait between requests.
    
    Returns:
        pd.DataFrame: A DataFrame with the combined toxin data.
    """
    all_toxins = []  # Lista para armazenar os resultados

    # Carrega os dados do CSV
    toxins_data = pd.read_csv('data/toxins_id.csv')

    # Converte 'cas_number' para string (para garantir que a comparação funcione corretamente)
    toxins_data['cas_number'] = toxins_data['cas_number'].astype(str)

    # Itera sobre a lista de cas_numbers
    for cas_number in cas_numbers:
        toxin_id_ = toxins_data.query(f"cas_number == '{cas_number}'")[['toxin_id']]
        #print(toxin_id_.loc[0, 'toxin_id']) 
        xml_content = fetch_toxin_xml(toxin_id_.loc[0, 'toxin_id'])
        if xml_content:  # Check if valid XML was fetched
            df_toxin = parse_xml_to_table(xml_content)
            all_toxins.append(df_toxin)
        
        # Delay between requests
        time.sleep(delay)

    # Concatenate all DataFrames, if available
    if all_toxins:
        return pd.concat(all_toxins, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an em

def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

_ = installff()
opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(options=opts)

def pubchem_extractor (cas_numbers):

    if isinstance(cas_numbers, str):
        cas_numbers = [cas_numbers]

    # Instalar o ChromeDriver automaticamente
    #chromedriver_autoinstaller.install()
    #driver = get_driver()

    # Inicializar o DataFrame final
    all_data = pd.DataFrame()

    for cas_number in cas_numbers:
        try:
            # Inicializar o navegador
            driver = webdriver.Chrome()
            
            # Acessar a página do PubChem
            url = 'https://pubchem.ncbi.nlm.nih.gov/'
            driver.get(url)

            time.sleep(3)
            
            # Inserir o número CAS na barra de pesquisa
            search = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div[2]/form/div/div[1]/input')
            search.send_keys(cas_number)
            search.send_keys(Keys.RETURN)

            # Aguardar até que o elemento clicável esteja disponível
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/main/div[2]/div[1]/div/div[2]/div/div[1]/div[2]/div[1]/a/span/span'))
            ).click()

            # Esperar para carregar os detalhes
            time.sleep(5)

            # Extração dos dados
            cid = driver.find_element(By.XPATH, '//div[text()="PubChem CID"]/following-sibling::div').text
            molecular_formula = driver.find_element(By.XPATH, '//div[text()="Molecular Formula"]/following-sibling::div').text
            synonyms = driver.find_element(By.XPATH, '//div[text()="Synonyms"]/following-sibling::div').text
            molecular_weight = driver.find_element(By.XPATH, '//div[text()="Molecular Weight"]/following-sibling::div').text
            dates = driver.find_element(By.XPATH, '//div[text()="Dates"]/following-sibling::div').text
            description = driver.find_element(By.XPATH, '//div[text()="Description"]/following-sibling::div').text

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
            all_data = pd.concat([all_data, data], ignore_index=True)

        except Exception as e:
            print(f"Erro ao processar o CAS Number {cas_number}: {e}")
        finally:
            # Fechar o navegador
            driver.quit()

    # Limpar o DataFrame final (remover caracteres indesejados)
    #all_data = all_data.applymap(lambda x: str(x).replace('\\n', ' ').replace('\n', ' ') if isinstance(x, str) else x)

    return all_data