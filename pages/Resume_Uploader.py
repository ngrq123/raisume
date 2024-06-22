import streamlit as st

from utils import document_parser

uploaded_file = st.file_uploader("Choose a docx/pdf file")
if uploaded_file is not None:
    content = document_parser.get_document_contents(uploaded_file)

    with st.expander('Extracted Content'):
        st.text(content)
