import os

from openai import AzureOpenAI
from dotenv import load_dotenv

import streamlit as st

load_dotenv()

# Load client
chat_client = AzureOpenAI(
  azure_endpoint=os.getenv('AOAI_ENDPOINT'),
  api_key=os.getenv('AOAI_KEY'),
  api_version=os.getenv('API_VERSION')
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": 'Hello 👋'})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message('user'):
        st.write(prompt)
    # Add message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Generate response and save
    with st.chat_message('assistant'):
        response_stream = chat_client.chat.completions.create(model=os.getenv('MODEL_NAME'), 
                                                              messages=[{'role': m['role'], 'content': m['content']} for m in st.session_state.messages], 
                                                              stream=True)
        response_message = st.write_stream(response_stream)
    st.session_state.messages.append({"role": "assistant", "content": response_message})