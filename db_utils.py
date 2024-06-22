import os
import pymongo
import logging

from pprint import pprint
from dotenv import load_dotenv
from models.skills import Skill

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hello_world():
    print("Hello World")


class CosmosDB_Utils:

    DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

    def __init__(self):
        self.client = pymongo.MongoClient(self.DB_CONNECTION_STRING)
        self.db = self.client.cosmic_works
        self.collection = None
        logger.info("Please create collection upon successful initialization.")

    ### Single Data ###
    def insert_single_data(self, data_obj):
        data_json = data_obj.model_dump(by_alias=True)
        inserted_id = self.collection.insert_one(data_json).inserted_id
        logger.info(f"Inserted hard skill with ID: {inserted_id}")


    def read_document(self, id):
        retrieved_document = self.collection.find_one({"id": id})

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


if __name__ == "__main__":

    # Initialize
    cosmosdb = CosmosDB_Utils()
    cosmosdb.collection = cosmosdb.db.skill

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

    # Read data
    retrieved_document = cosmosdb.read_document("1")
    retrieved_skill = Skill(**retrieved_document)
    # Print the retrieved product
    print("\nCast Skill from document:")
    print(retrieved_skill)

    # Drop Collection
    cosmosdb.drop_db_collection("skill")


