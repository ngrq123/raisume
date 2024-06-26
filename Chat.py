import json
import os

from db_utils import CosmosDB_Utils
from utils import llm_utils, prompt_utils

import streamlit as st

st.set_page_config(layout='wide')

chat_client = llm_utils.get_openai_client()

# Initialize DB_Utils
cosmosdb = CosmosDB_Utils()
cosmosdb.collection = cosmosdb.db.skill

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

    system_prompt = prompt_utils.get_first_system_prompt()
    st.session_state.messages.append({"role": "system", "content": system_prompt})
    
    st.session_state.messages.append({"role": "assistant", "content": 'Hello 👋'})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"] if message['role'] != 'system' else 'assistant'):
        st.write(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message('user'):
        st.write(prompt)
    # Add message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Generate response and save
    with st.chat_message('assistant'):
        response_stream = llm_utils.get_llm_response(chat_client, st.session_state.messages, stream=True)
        response = st.write_stream(response_stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
