# import chromedriver_autoinstaller
import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

firefoxOptions = Options()
firefoxOptions.add_argument("--headless")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(
    options=firefoxOptions,
    service=service,
)


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
    toxins_data = pd.read_csv("data/toxins_id.csv")

    # Converte 'cas_number' para string (para garantir que a comparação funcione corretamente)
    toxins_data["cas_number"] = toxins_data["cas_number"].astype(str)

    # Itera sobre a lista de cas_numbers
    for cas_number in cas_numbers:
        toxin_id_ = toxins_data.query(f"cas_number == '{cas_number}'")[["toxin_id"]]
        # print(toxin_id_.loc[0, 'toxin_id'])
        xml_content = fetch_toxin_xml(toxin_id_.loc[0, "toxin_id"])
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


def pubchem_extractor(cas_numbers):

    if isinstance(cas_numbers, str):
        cas_numbers = [cas_numbers]

    # Instalar o ChromeDriver automaticamente
    # chromedriver_autoinstaller.install()
    # driver = get_driver()

    # Inicializar o DataFrame final
    all_data = pd.DataFrame()

    for cas_number in cas_numbers:
        try:
            # Inicializar o navegador
            # driver = webdriver.Chrome()

            # Acessar a página do PubChem
            url = "https://pubchem.ncbi.nlm.nih.gov/"
            driver.get(url)

            time.sleep(3)

            # Inserir o número CAS na barra de pesquisa
            search = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div[2]/form/div/div[1]/input",
            )
            search.send_keys(cas_number)
            search.send_keys(Keys.RETURN)

            # Aguardar até que o elemento clicável esteja disponível
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div/main/div[2]/div[1]/div/div[2]/div/div[1]/div[2]/div[1]/a/span/span",
                    )
                )
            ).click()

            # Esperar para carregar os detalhes
            time.sleep(5)

            # Extração dos dados
            cid = driver.find_element(
                By.XPATH, '//div[text()="PubChem CID"]/following-sibling::div'
            ).text
            molecular_formula = driver.find_element(
                By.XPATH, '//div[text()="Molecular Formula"]/following-sibling::div'
            ).text
            synonyms = driver.find_element(
                By.XPATH, '//div[text()="Synonyms"]/following-sibling::div'
            ).text
            molecular_weight = driver.find_element(
                By.XPATH, '//div[text()="Molecular Weight"]/following-sibling::div'
            ).text
            dates = driver.find_element(
                By.XPATH, '//div[text()="Dates"]/following-sibling::div'
            ).text
            description = driver.find_element(
                By.XPATH, '//div[text()="Description"]/following-sibling::div'
            ).text

            # Criar um dicionário com os dados extraídos
            dict_data = {
                "CAS Number": [cas_number],
                "CID": [cid],
                "Fórmula Molecular": [molecular_formula],
                "Sinônimos": [synonyms],
                "Peso Molecular": [molecular_weight],
                "Datas": [dates],
                "Descrição": [description],
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
    # all_data = all_data.applymap(lambda x: str(x).replace('\\n', ' ').replace('\n', ' ') if isinstance(x, str) else x)

    return all_data


def echa_extrator(cas_numbers):

    if isinstance(cas_numbers, str):
        cas_numbers = [cas_numbers]

    all_data = pd.DataFrame()

    # Acessar a página do PubChem
    url = "https://echa.europa.eu/pt/information-on-chemicals"
    driver.get(url)

    for cas_number in cas_numbers:
        try:
            # Configurar WebDriverWait
            wait = WebDriverWait(driver, 10)
            actions = ActionChains(driver)

            # Aguarde o botão de aceitar cookies estar clicável
            cookie_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="cookie-consent-banner"]/div/div/div[2]/a[1]')
                )
            )
            actions.move_to_element(cookie_button).click().perform()

            time.sleep(2)
            # Localizar o checkbox pelo id
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

            time.sleep(3)
            search = driver.find_element(
                By.XPATH, '//*[@id="autocompleteKeywordInput"]'
            )
            search.send_keys(cas_number)

            search.send_keys(Keys.RETURN)

            # Aguardar até que o elemento esteja visível e clicável
            try:
                # Substitua o tempo de espera conforme necessário (em segundos)
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            '//*[@id="_disssimplesearch_WAR_disssearchportlet_rmlSearchResultVOsSearchContainerSearchContainer"]/table/tbody/tr[1]/td[1]/a',
                        )
                    )
                )
                # Clica no elemento
                element.click()
                print("Elemento clicado com sucesso!")
            except Exception as e:
                print(f"Erro ao localizar ou clicar no elemento: {e}")  # send.click()

            time.sleep(5)
            # Extração de informações específicas

            ec = driver.find_element(
                By.XPATH,
                '//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[1]/div/div/div/p[1]',
            ).text
            cas = driver.find_element(
                By.XPATH,
                '//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[1]/div/div/div/p[3]',
            ).text
            molecular_formula = driver.find_element(
                By.XPATH,
                '//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[1]/div/div/div/p[3]',
            ).text
            haz_classification_laballing = driver.find_element(
                By.XPATH,
                '//*[@id="infocardContainer"]/div/div[1]/div/div[1]/div/div[2]/div/div/div/p',
            ).text
            about_1 = driver.find_element(
                By.XPATH, '//*[@id="aboutSubstanceParagraphWrapper"]/p[1]'
            ).text
            about_2 = driver.find_element(
                By.XPATH, '//*[@id="aboutSubstanceParagraphWrapper"]/p[2]'
            ).text
            consumer_user = driver.find_element(
                By.XPATH, '//*[@id="aboutSubstanceParagraphWrapper"]/p[3]'
            ).text
            article_services = driver.find_element(
                By.XPATH, '//div[text()="Description"]/following-sibling::div'
            ).text

            # Criar um dicionário com os dados extraídos
            dict_data = {
                "ec": [ec],
                "Cas Number": [cas],
                "Fórmula Molecular": [molecular_formula],
                "HAZ Class.": [haz_classification_laballing],
                "About": [about_1],
                "About 2": [about_2],
                "Consumer User": [consumer_user],
                "article_services": [article_services],
            }

            # Criar um DataFrame e adicionar ao DataFrame final
            data = pd.DataFrame(dict_data)
            all_data = pd.concat([all_data, data], ignore_index=True)

        except Exception as e:
            print(f"Erro ao processar o CAS Number {cas_number}: {e}")
        finally:
            # Fechar o navegador
            driver.quit()
