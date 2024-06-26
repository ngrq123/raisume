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
required_fields = [
    "sourceDisplayName", "shortDescription", 'longDescription'
]

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []
    system_prompt = prompt_utils.get_first_system_prompt()
    st.session_state.messages.append({"role": "system", "content": system_prompt, 'from_chat': True})
    st.session_state.messages.append({"role": "assistant", "content": 'Hello 👋', 'from_chat': True})

# Display chat messages (from history on app rerun)
chat_messages = list(filter(lambda m: 'from_chat' in m and m['from_chat'], st.session_state.messages))
for message in chat_messages:
    if message['role'] == 'system':
        with st.chat_message('assistant'):
            with st.expander('System Prompt', expanded=False):
                st.write(message['content'])
    else:
        with st.chat_message(message['role']):
            st.write(message['content'])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message('user'):
        st.write(prompt)
    # Add message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, 'from_chat': True})

    rag_results = cosmosdb.get_grounding_data_from_vector_search('skill', prompt, num_results=50, required_fields=required_fields)
    st.session_state.messages.append({'role': 'system', 'content': rag_results})
    with st.chat_message('assistant'):
            with st.expander('System Prompt', expanded=False):
                st.write(rag_results)

    # Generate response and save
    chat_messages = list(filter(lambda m: 'from_chat' in m and m['from_chat'], st.session_state.messages))
    with st.chat_message('assistant'):
        response_stream = llm_utils.get_llm_response(chat_client, chat_messages, stream=True)
        response = st.write_stream(response_stream)
        st.session_state.messages.append({"role": "assistant", "content": response, 'from_chat': True})
