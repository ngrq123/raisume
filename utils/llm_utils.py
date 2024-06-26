import os

from dotenv import load_dotenv
from openai import AzureOpenAI

def get_openai_client():
    load_dotenv()

    # Load client
    chat_client = AzureOpenAI(
        azure_endpoint=os.getenv('AOAI_ENDPOINT'),
        api_key=os.getenv('AOAI_KEY'),
        api_version=os.getenv('AOAI_API_VERSION')
    )

    return chat_client


def get_llm_response(chat_client, messages, response_format='auto', stream=False):
    load_dotenv('..')

    response = chat_client.chat.completions.create(messages=[{'role': m['role'], 'content': m['content']} for m in messages], 
                                        model=os.getenv('MODEL_NAME'),
                                        response_format=response_format,
                                        stream=stream)
    
    # if isinstance(response_format, dict) and response_format['type'] == 'json_object':
        # Check if valid json
        # valid_json = False
        # while not valid_json:
        #     # response = chat_client.chat.completions.create(messages=[{'role': m['role'], 'content': m['content']} for m in message_history], 
        #     #                                             model=os.getenv('MODEL_NAME'), 
        #     #                                             response_format={'type': 'json_object'},
        #     #                                             stream=False)
        #     # response_message = response.choices[0].message.content

        #     response = (chat_client, message_history, stream=True)
        #     response_message = response.choices[0].message.content
            
        #     try:
        #         json.loads(response_message)
        #         valid_json = True
        #     except ValueError:
        #         continue
        # st.json(response_message)

    return response