import os
import json
import pymongo
import logging
from typing import List
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import AzureCosmosDBVectorSearch
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import Tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain_core.messages import SystemMessage

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangChain_Utils():

    def __init__(self, db_collection_namespace):

        self.DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
        self.EMBEDDINGS_DEPLOYMENT_NAME = os.environ.get("EMBEDDINGS_DEPLOYMENT_NAME")
        self.COMPLETIONS_DEPLOYMENT_NAME = os.environ.get("COMPLETIONS_DEPLOYMENT_NAME")
        self.AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")
        self.AOAI_API_KEY = os.environ.get("AOAI_KEY")
        self.AOAI_API_VERSION = os.environ.get("AOAI_API_VERSION")

        self.llm = AzureChatOpenAI(            
            temperature = 0,
            openai_api_version = self.AOAI_API_VERSION,
            azure_endpoint = self.AOAI_ENDPOINT,
            openai_api_key = self.AOAI_API_KEY,         
            azure_deployment = self.COMPLETIONS_DEPLOYMENT_NAME
        )
        self.embedding_model = AzureOpenAIEmbeddings(
            openai_api_version = self.AOAI_API_VERSION,
            azure_endpoint = self.AOAI_ENDPOINT,
            openai_api_key = self.AOAI_API_KEY,   
            azure_deployment = self.EMBEDDINGS_DEPLOYMENT_NAME,
            chunk_size=10
        )
        self.db_collection_namespace = db_collection_namespace
        self.vector_store = AzureCosmosDBVectorSearch.from_connection_string(
            connection_string = self.DB_CONNECTION_STRING,
            namespace = self.db_collection_namespace,
            embedding = self.embedding_model,
            index_name = "VectorSearchIndex",    
            embedding_key = "contentVector",
            text_key = "_id"
        )
        self.retriever = self.vector_store.as_retriever()


    def format_docs(self, docs:List[Document]) -> str:
        """
        Prepares the product list for the system prompt.
        """
        str_docs = []
        for doc in docs:
            # Build the product document without the contentVector
            doc_dict = {"_id": doc.page_content}
            doc_dict.update(doc.metadata)
            if "contentVector" in doc_dict:  
                del doc_dict["contentVector"]
            str_docs.append(json.dumps(doc_dict, default=str))                  
        # Return a single string containing each product JSON representation
        # separated by two newlines
        return "\n\n".join(str_docs)

    def query_vector_store(self, query, k=3):
        # Ensure the query is a string
        if not isinstance(query, str):
            raise ValueError("Query must be a string")
        return self.vector_store.similarity_search(query, k=k)


if __name__ == '__main__':
    
    # Initialize LangChain_Utils
    skill_langchain = LangChain_Utils("cosmic_works.skill")

    # Test Query
    query = "What is data science?"
    try:
        # results = skill_langchain.query_vector_store(query)
        results = skill_langchain.vector_store.similarity_search_with_score(query)
        for result in results:
            print(result)
    except Exception as e:
        print(f"Error: {e}")