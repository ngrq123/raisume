import os
import pymongo
import logging

from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hello_world():
    print("Hello World")


class CosmosDB_Utils:

    DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

    def __init__(self):
        client = pymongo.MongoClient(self.DB_CONNECTION_STRING)
        self.db = client.cosmic_works
        self.collection = None
        logger.info("Please create collection upon successful initialization.")

    ### Single Data ###
    def insert_single_data(self, data_json):
        inserted_id = self.collection.insert_one(data_json).inserted_id
        logger.info(f"Inserted hard skill with ID: {inserted_id}")


    def read_document(self, id):
        retrieved_document = self.collection.find_one({"id": id})

        logger.info("JSON Document retrieved from the database!")
        pprint(retrieved_document)

        return retrieved_document

    
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

if __name__ == "__main__":
    cosmosdb = CosmosDB_Utils()
    cosmosdb.collection = cosmosdb.hard_skills