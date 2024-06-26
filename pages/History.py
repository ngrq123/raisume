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
            skill_flattened[str(key).title().replace('_', ' ')] = value
        skills_flattened.append(skill_flattened)
    return pd.DataFrame.from_records(skills_flattened)


st.header('Message History')

has_history = ('messages' in st.session_state)

if not has_history:
    st.write('There are no messages. Interact with the chat first.')

if has_history:
    for m in st.session_state.messages:
        role, content = m['role'], m['content']
        
        if role == 'user':
            with st.chat_message('user'):
                    st.write(content)
        
        if role == 'assistant':
            with st.chat_message('assistant'):
                try:
                    _json = json.loads(content)
                    st.subheader('Skills Identified by Gen AI')
                    st.dataframe(skills_json_to_df(_json, 'skills'), hide_index=True)
                    st.subheader('Predicted Skills by Gen AI')
                    st.dataframe(skills_json_to_df(_json, 'predicted_skills'), hide_index=True)
                except JSONDecodeError:
                    st.write(content)

        if role == 'system':
            with st.chat_message('assistant'):
                with st.expander('System Prompt'):
                    st.write(content)
