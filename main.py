import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import time

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

def process_toxins(toxin_ids, delay=1):
    """
    Process a list of toxin IDs and fetch their data with a delay between requests.
    
    Args:
        toxin_ids (list): List of toxin IDs to process.
        delay (int or float): Time in seconds to wait between requests.
    
    Returns:
        pd.DataFrame: A DataFrame with the combined toxin data.
    """
    all_toxins = []

    for toxin_id in toxin_ids:
        xml_content = fetch_toxin_xml(toxin_id)
        if xml_content:  # Check if valid XML was fetched
            df_toxin = parse_xml_to_table(xml_content)
            all_toxins.append(df_toxin)
        
        # Delay between requests
        time.sleep(delay)

    # Concatenate all DataFrames, if available
    if all_toxins:
        return pd.concat(all_toxins, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data was fetched

def main():

    st.sidebar.image('images/Logo_BioScient_colorido_2.png', use_container_width=True)

    # Conteúdo principal
    st.title('TOXBASE - Toxin Information Fetcher')

    # Campo de texto para entrada dos IDs de toxinas
    toxin_input = st.text_area("Enter Toxin IDs (comma-separated):", "")

    if toxin_input:
        toxin_ids = [x.strip() for x in toxin_input.split(",")]

        if st.button('Find Toxins'):
            with st.spinner("Fetching data..."):
                result = process_toxins(toxin_ids, delay=1)

            if not result.empty:
                st.success(f"Found data for {len(result)} toxins!")
                st.dataframe(result)
            else:
                st.warning("No data found for the provided IDs.")

if __name__ == "__main__":
    main()
