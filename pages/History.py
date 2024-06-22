from json import JSONDecodeError
import json

import pandas as pd
import streamlit as st


def skills_json_to_df(_json, key):
    skills = _json[key]
    skills_flattened = []
    for skill in skills:
        skill_flattened = dict()
        for key, value in skill.items():
            if isinstance(value, list):
                value = ' | '.join(value)
            skill_flattened[key] = value
        skills_flattened.append(skill_flattened)
    return pd.DataFrame.from_records(skills_flattened)


st.header('Message History')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

    _file = open('.\prompt_templates\system_prompt.txt', 'r', encoding='utf-8')
    system_prompt = _file.read()
    _file.close()
    st.session_state.messages.append({"role": "system", "content": system_prompt})
    
    st.session_state.messages.append({"role": "assistant", "content": 'Hello 👋'})

has_history = False
for idx, m in enumerate(st.session_state.messages):
    role, content = m['role'], m['content']
    # Get previous message
    previous_message = st.session_state.messages[idx-1]
    if role == 'assistant' and previous_message['role'] == 'user':  # Only process if previous message is user and current message is assistant
            has_history = True
            with st.chat_message('user'):
                st.write(previous_message['content'])
            try:
                _json = json.loads(content)
                if 'skills' in _json:
                    df = skills_json_to_df(_json, 'skills')
                    expander = st.expander('Skills', expanded=True)
                    expander.dataframe(df, hide_index=True)
                if 'predicted_skills' in _json:
                    skills_json_to_df(_json, 'predicted_skills')
                    expander = st.expander('Predicted Skills', expanded=True)
                    expander.dataframe(df, hide_index=True)
            except JSONDecodeError:
                continue

if not has_history:
    st.write('There are no messages. Interact with the chat first.')