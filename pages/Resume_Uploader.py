import json

import pandas as pd
import streamlit as st

from utils import document_utils, llm_utils, prompt_utils
from db_utils import CosmosDB_Utils

st.set_page_config(layout='wide')


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


llm_client = llm_utils.get_openai_client()
first_system_prompt = prompt_utils.get_first_system_prompt(output_format='json')
messages=[{'role': 'system', 'content': first_system_prompt}]

# Initialize DB_Utils
cosmosdb = CosmosDB_Utils()
cosmosdb.collection = cosmosdb.db.skill
required_fields = [
    "sourceDisplayName", "shortDescription", 'longDescription'
]

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Choose a docx/pdf file")
if uploaded_file is not None:
    content = document_utils.get_document_contents(uploaded_file)

    with st.expander('Extracted Content', expanded=False):
        st.text(content)
    messages.append({'role': 'user', 'content': content})

    rag_results = cosmosdb.get_grounding_data_from_vector_search('skill', content, num_results=50, required_fields=required_fields)
    messages.append({'role': 'system', 'content': rag_results})
    
    response = llm_utils.get_llm_response(llm_client,
                                          messages,
                                          response_format={'type': 'json_object'})
    
    response = response.choices[0].message.content
    _json = json.loads(response)
    st.subheader('Skills Identified by Gen AI')
    st.dataframe(skills_json_to_df(_json, 'skills'), hide_index=True)
    st.subheader('Predicted Skills by Gen AI')
    st.dataframe(skills_json_to_df(_json, 'predicted_skills'), hide_index=True)
    messages.append({'role': 'assistant', 'content': response})

    st.session_state.messages += messages
