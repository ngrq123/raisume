import os
import pymongo
import time
import logging
import json

from pprint import pprint
from dotenv import load_dotenv
from openai import AzureOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from models.skills import Skill

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CosmosDB_Utils:

    def __init__(self):
        self.DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
        self.AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")
        self.AOAI_KEY = os.environ.get("AOAI_KEY")
        self.AOAI_API_VERSION = os.environ.get("AOAI_API_VERSION")
        self.EMBEDDINGS_DEPLOYMENT_NAME = os.environ.get("EMBEDDINGS_DEPLOYMENT_NAME")
        self.client = pymongo.MongoClient(self.DB_CONNECTION_STRING)
        self.db = self.client.cosmic_works
        self.collection = None
        self.ai_client = AzureOpenAI(
            azure_endpoint = self.AOAI_ENDPOINT,
            api_version = self.AOAI_API_VERSION,
            api_key = self.AOAI_KEY
        )
        logger.info("Please create collection upon successful initialization.")


    ### Single Data ###
    def insert_single_data(self, data_obj):
        data_json = data_obj.model_dump(by_alias=True)
        inserted_id = self.collection.insert_one(data_json).inserted_id
        logger.info(f"Inserted hard skill with ID: {inserted_id}")


    def read_document(self, field_name, field_val):
        retrieved_document = self.collection.find_one({f"{field_name}": field_val})
        logger.info("JSON Document retrieved from the database!")
        pprint(retrieved_document)
        return retrieved_document

    
    def count_documents_in_collection(self):
        print(f"Number of documents in the collection: {self.collection.count_documents({})}")

    
    def update_single_data(self, id_dict, update_dict):
        update_result = self.collection.find_one_and_update(
            id_dict,
            {"$set" : update_dict},
            return_document=pymongo.ReturnDocument.AFTER
        )
        logger.info("Updated JSON document:")
        logger.info(update_result)
    

    def delete_single_data(self, id_dict):
        delete_result = self.collection.delete_one(id_dict)
        logger.info(f"Deleted documents count: {delete_result.deleted_count}")
        logger.info(f"Number of documents in the collection: {self.collection.count_documents({})}")


    ### Bulk Data ###
    def bulk_upsert_data(self, list_of_data):
        self.collection.bulk_write(
            [
                pymongo.UpdateOne(
                    {"id" : data.id},
                    {"$set" : data.model_dump(by_alias=True)}
                    , upsert=True
                )
                for data in list_of_data
            ]
        )
        logger.info("Bulk upsert completed.")

    
    ### Clean Up ###
    def drop_db_collection(self, collection_name):
        self.db.drop_collection(collection_name)
        logger.info("Collection Dropped")


    def drop_client_database(self, db_name):
        self.client.drop_database(db_name)
        logger.info("Database Dropped")


    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def generate_embeddings(self, text: str):
        '''
        Generate embeddings from string of text using the deployed Azure OpenAI API embeddings model.
        This will be used to vectorize document data and incoming user messages for a similarity search with
        the vector index.
        '''
        response = self.ai_client.embeddings.create(input=text, model=self.EMBEDDINGS_DEPLOYMENT_NAME)
        embeddings = response.data[0].embedding
        time.sleep(0.5) # rest period to avoid rate limiting on AOAI
        return embeddings

    
    def add_collection_content_vector_field(self, collection_name: str):
        '''
        Add a new field to the collection to hold the vectorized content of each document.
        '''
        collection = self.db[collection_name]
        
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
    

    def create_vector_index(self, collection_name):
        self.db.command({
            'createIndexes': collection_name,
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


    def drop_index(self, collection_name, index_name):
        try:
            collection = self.db[collection_name]
            collection.drop_index(index_name)
            logger.info(f"Index {index_name} dropped from the {collection_name} collection")
        except Exception as e:
            logger.error(f"Error dropping index {index_name} from the {collection_name} collection: {e}")



    ### Vector Search ###
    def vector_search(self, collection_name, query, num_results=3):
        """
        Perform a vector search on the specified collection by vectorizing
        the query and searching the vector index for the most similar documents.

        returns a list of the top num_results most similar documents
        """
        collection = self.db[collection_name]
        query_embedding = self.generate_embeddings(query)    
        pipeline = [
            {
                '$search': {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": "contentVector",
                        "k": num_results
                    },
                    "returnStoredSource": True }},
            {'$project': { 'similarityScore': { '$meta': 'searchScore' }, 'document' : '$$ROOT' } }
        ]
        results = collection.aggregate(pipeline)
        return results

    def print_vector_search_result(self, result, list_of_document_fields):
        print(f"_id: {result['document']['_id']}\n")
        print(f"Similarity Score: {result['similarityScore']}") 
        for field in list_of_document_fields:
            print(f"{field}: {result['document'][field]}")

if __name__ == "__main__":

    ### TEST DB CRUD ###
    # # Initialize
    # cosmosdb = CosmosDB_Utils()
    # cosmosdb.collection = cosmosdb.db.test

    # # Sample Data
    # sample_skill = Skill(
    #     id = "0",
    #     skill = ".net",
    #     aliases = None,
    #     source_id = "stackshare..net",
    #     display_name = ".NET",
    #     shortDescription = ".NET is a free, cross-platform, open source developer platform for building many different types of applications.",
    #     longDescription = ".NET is a general purpose development platform. With .NET, you can use multiple languages, editors, and libraries to build native applications for web, mobile, desktop, gaming, and IoT for Windows, macOS, Linux, Android, and more.",
    #     sourceURL = "http://www.microsoft.com/net/"
    # )

    # # Insert data
    # cosmosdb.insert_single_data(sample_skill)

    # # Read data
    # retrieved_document = cosmosdb.read_document(".net")
    # retrieved_skill = Skill(**retrieved_document)
    # # Print the retrieved product
    # print("\nCast Skill from document:")
    # print(retrieved_skill)

    # # Drop Collection
    # cosmosdb.drop_db_collection("test")

    ### TEST DB VECTOR SEARCH ###
    # Initialize
    cosmosdb = CosmosDB_Utils()
    cosmosdb.collection = cosmosdb.db.skill

    # Vector Search
    query = "What is data science?"
    results = cosmosdb.vector_search("skill", query, num_results=4)

    for result in results['document'].items():
        print(result)



