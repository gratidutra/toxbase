import streamlit as st

from extractors.extractor import pubchem_extractor, echa_extractor


def main():

    st.sidebar.image("images/Logo_BioScient_colorido_2.png", use_container_width=True)
    st.sidebar.markdown(
        """:red-background[Toxin Information Fetcher é uma aplicação desenvolvida para facilitar a busca e recuperação de \n informações toxicológicas a partir de IDs, CAS ou nomes específicos de toxinas. \n A interface intuitiva permite aos usuários inserir múltiplos IDs, CAS ou nomes de toxinas.]\n """
    )

    # Conteúdo principal
    st.title("TOXBASE - Toxin Information Fetcher")

    # Campo de texto para entrada dos IDs de toxinas

    database_functions = {
        # "T3DB": t3db_extractor,
        "PubChem": pubchem_extractor,
        "ECHA": echa_extractor,
    }

    # Entrada de IDs e seleção de bancos
    cas_input = st.text_area("Enter CAS Number (comma-separated):", "")
    selected_databases = st.multiselect(
        "Select Databases to Extract From:",
        options=list(database_functions.keys()),
        default=list(database_functions.keys()),  # Pré-seleciona todos os bancos
    )

    if cas_input:
        cas_ids = [x.strip() for x in cas_input.split(",") if x.strip()]

    if st.button("Find Toxins"):
        if not selected_databases:
            st.warning("Please select at least one database.")
        else:
            with st.spinner("Fetching data from selected databases..."):
                results = {}
                for db in selected_databases:
                    extractor = database_functions[db]
                    results[db] = extractor(cas_ids)

            # Exibe os resultados em abas
            if results:
                tabs = st.tabs(selected_databases)
                for i, db in enumerate(selected_databases):
                    with tabs[i]:
                        st.subheader(f"Results from {db}")
                        if not results[db].empty:
                            st.dataframe(results[db])
                        else:
                            st.warning(f"No data found in {db}.")
    else:
        st.info("Please enter toxin IDs in the text area above.")


if __name__ == "__main__":
    main()
