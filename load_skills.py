import json
import logging
import sys
import os

from models.skills import Skill
from db_utils import CosmosDB_Utils
from data_utils import Data_Utils
# from vector_store_utils import VectorStore_Utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data_utils = Data_Utils()

# Constants
SKILLS_JSON_DIR = os.path.join('./assets', 'skills.json')

# Load in the skills
skill_dict = data_utils.read_json(SKILLS_JSON_DIR)
logger.info('Skills JSON loaded into Python. Processing...')


# Process the skills dictionary
list_of_skills = data_utils.process_skill_dict(skill_dict)

# Initialize the DB
logger.info('Initialize CosmosDB instance')
cosmosdb = CosmosDB_Utils()
# cosmosdb.drop_db_collection("skill")
cosmosdb.collection = cosmosdb.db.skill

# Bulk Insertion
logger.info('Loading skills data into CosmosDB')
cosmosdb.bulk_upsert_data(list_of_skills)

# Vectorize and store embeddings in each document
# Create vector field for each document
cosmosdb.add_collection_content_vector_field("skill")

# Create vector index for collection
cosmosdb.create_vector_index("skill")
