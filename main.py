import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
import extractor_page

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    st.markdown(
            f"""
            <style>
                .top-right {{
                    position: absolute;
                    top: 10px;
                    right: 20px;
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                    font-size: 16px;
                    z-index: 1000;
                }}
            </style>
            <div class="top-right">
                👋 Welcome, <strong>{st.session_state["name"]}</strong>!
            </div>
            </br>
            """, unsafe_allow_html=True
        )
    st.write('___')
    extractor_page.extractor_page()
    authenticator.logout('Logout', 'sidebar')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
