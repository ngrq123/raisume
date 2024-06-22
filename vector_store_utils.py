import os
import pymongo
import time
import json
import logging

from db_utils import CosmosDB_Utils
from models.skills import Skill
from openai import AzureOpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class VectorStore_Utils():

    CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
    EMBEDDINGS_DEPLOYMENT_NAME = os.environ.get("EMBEDDINGS_DEPLOYMENT_NAME")
    COMPLETIONS_DEPLOYMENT_NAME = os.environ.get("COMPLETIONS_DEPLOYMENT_NAME")
    AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")
    AOAI_API_KEY = os.environ.get("AOAI_KEY")
    AOAI_API_VERSION = os.environ.get("AOAI_API_VERSION")
    
    def __init__(self):

        self.ai_client = AzureOpenAI(
            azure_endpoint = self.AOAI_ENDPOINT,
            api_version = self.AOAI_API_VERSION,
            api_key = self.AOAI_API_KEY
        )

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def generate_embeddings(self, text: str):
        '''
        Generate embeddings from string of text using the deployed Azure OpenAI API embeddings model.
        This will be used to vectorize document data and incoming user messages for a similarity search with
        the vector index.
        '''
        try:
            response = self.ai_client.embeddings.create(input=text, model=self.EMBEDDINGS_DEPLOYMENT_NAME)
            embeddings = response.data[0].embedding
            time.sleep(0.5) # rest period to avoid rate limiting on AOAI
            return embeddings

        except httpx.HTTPStatusError as http_err:
            if http_err.response.status_code == 429: # Too Many Requests
                retry_after = int(http_err.response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                return self.generate_embeddings(text) # Retry after delay
            else:
                raise
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise 
    

    # def add_collection_content_vector_field(self, collection_name: str, db):
    #     '''
    #     Add a new field to the collection to hold the vectorized content of each document.
    #     '''
    #     collection = db[collection_name]
    #     bulk_operations = []
    #     try:
    #         with collection.find({}, no_cursor_timeout=True) as cursor:
    #             # for doc in collection.find():
    #             for doc in cursor:
    #                 # remove any previous contentVector embeddings
    #                 if "contentVector" in doc:
    #                     del doc["contentVector"]

    #                 # generate embeddings for the document string representation
    #                 content = json.dumps(doc, default=str)
    #                 content_vector = self.generate_embeddings(content)       
                    
    #                 bulk_operations.append(pymongo.UpdateOne(
    #                     {"_id": doc["_id"]},
    #                     {"$set": {"contentVector": content_vector}},
    #                     upsert=True
    #                 ))
    #             # execute bulk operations
    #             collection.bulk_write(bulk_operations)
    #             logger.info(f"Vector field created for the {collection_name} collection")
        
    #     except pymongo.errors.CursorNotFound:
    #         logger.error("Cursor expired. Handle accordingly.")
    #     except Exception as e:
    #         logger.error(f"Error processing documents: {e}")
    #     finally:
    #         cursor.close()

    def add_collection_content_vector_field(self, collection_name: str, db):
        '''
        Add a new field to the collection to hold the vectorized content of each document.
        '''
        collection = db[collection_name]
        
        def process_documents(skip_count=0):
            try:
                with collection.find({}, no_cursor_timeout=True).skip(skip_count) as cursor:
                    for doc in cursor:
                        # Remove any previous contentVector embeddings
                        if "contentVector" in doc:
                            del doc["contentVector"]

                        # Generate embeddings for the document string representation
                        content = json.dumps(doc, default=str)
                        content_vector = self.generate_embeddings(content)

                        collection.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"contentVector": content_vector}},
                            upsert=True
                        )
                        
                        # Keep track of processed documents
                        skip_count += 1

            except pymongo.errors.CursorNotFound:
                logger.error("Cursor expired. Resuming from last processed document.")
                process_documents(skip_count)  # Recursively continue from the last processed document
            except Exception as e:
                logger.error(f"Error processing documents: {e}")
                raise

        # Start processing documents
        process_documents()

    
    def create_vector_index(self, collection_name, db):
        db.command({
            'createIndexes': 'products',
            'indexes': [
                {
                    'name': 'VectorSearchIndex',
                    'key': {
                        "contentVector": "cosmosSearch"
                },
                'cosmosSearchOptions': {
                    'kind': 'vector-ivf',
                    'numLists': 1,
                    'similarity': 'COS',
                    'dimensions': 1536
                    }
                }
            ]
        })
        logger.info(f"Vector index created for the {collection_name} collection")

if __name__ == "__main__":

    # Initialize
    cosmosdb = CosmosDB_Utils()
    cosmosdb.collection = cosmosdb.db.test

    # Sample Data
    sample_skill = Skill(
        id = "1",
        skill = ".net",
        aliases = None,
        source_id = "stackshare..net",
        display_name = ".NET",
        shortDescription = ".NET is a free, cross-platform, open source developer platform for building many different types of applications.",
        longDescription = ".NET is a general purpose development platform. With .NET, you can use multiple languages, editors, and libraries to build native applications for web, mobile, desktop, gaming, and IoT for Windows, macOS, Linux, Android, and more.",
        sourceURL = "http://www.microsoft.com/net/"
    )

    # Insert data
    cosmosdb.insert_single_data(sample_skill)

    # # Read data
    # retrieved_document = cosmosdb.read_document(".net")
    # retrieved_skill = Skill(**retrieved_document)
    # # Print the retrieved product
    # print("\nCast Skill from document:")
    # print(retrieved_skill)

    # Initialize Vector Store
    vector_store = VectorStore_Utils()

    # Create vector field for each document
    vector_store.add_collection_content_vector_field("test", cosmosdb.db)

    # # Read data
    # retrieved_document = cosmosdb.read_document(".net")
    # retrieved_skill = Skill(**retrieved_document)
    # # Print the retrieved product
    # print("\nCast Skill from document:")
    # print(retrieved_skill)

    # Create vector index for collection
    vector_store.create_vector_index("test", cosmosdb.db)

    # Drop Collection
    cosmosdb.drop_db_collection("test")



