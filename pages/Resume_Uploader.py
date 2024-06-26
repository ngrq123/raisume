import streamlit as st

from utils import document_utils, llm_utils, prompt_utils

st.set_page_config(layout='wide')

llm_client = llm_utils.get_openai_client()
first_system_prompt = prompt_utils.get_first_system_prompt(output_format='json')

uploaded_file = st.file_uploader("Choose a docx/pdf file")
if uploaded_file is not None:
    content = document_utils.get_document_contents(uploaded_file)

    with st.expander('Extracted Content', expanded=False):
        st.text(content)

    
