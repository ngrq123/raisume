import requests
import streamlit as st

content = requests.get('https://raw.githubusercontent.com/ngrq123/raisume/main/README.md').text
content = content.replace('./images/', 'https://raw.githubusercontent.com/ngrq123/raisume/main/images/')
st.markdown(content, unsafe_allow_html=True)