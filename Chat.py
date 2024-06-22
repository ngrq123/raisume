import os

from openai import AzureOpenAI
from dotenv import load_dotenv

import streamlit as st

load_dotenv()
st.set_page_config(layout='wide')

# Load client
chat_client = AzureOpenAI(
  azure_endpoint=os.getenv('AOAI_ENDPOINT'),
  api_key=os.getenv('AOAI_KEY'),
  api_version=os.getenv('API_VERSION')
)

_file = open('.\prompt_templates\system_prompt.txt', 'r', encoding='utf-8')
system_prompt = _file.read()
_file.close()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": system_prompt})
    st.session_state.messages.append({"role": "assistant", "content": 'Hello 👋'})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"] if message['role'] != 'system' else 'assistant'):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message('user'):
        st.markdown(prompt)
    # Add message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Generate response and save
    with st.chat_message('assistant'):
        response = chat_client.chat.completions.create(messages=[{'role': m['role'], 'content': m['content']} for m in st.session_state.messages], 
                                                       model=os.getenv('MODEL_NAME'), 
                                                       response_format={'type': 'json_object'},
                                                       stream=False)
        response_message = response.choices[0].message.content
        st.json(response_message)
    st.session_state.messages.append({"role": "assistant", "content": response_message})
