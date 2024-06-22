import pandas as pd
import json
import logging

from models.skills import Skill
from db_utils import CosmosDB_Utils
from vector_store_utils import VectorStore_Utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load in the skills
with open('./assets/skills.json') as f:
    skill_dict = json.load(f)
logger.info('Skills JSON loaded into Python. Processing...')


# Process the skills dictionary
list_of_skills = []
id_counter = 0
for skill_name, info in skill_dict.items():
    aliases = info.get('aliases', [])
    sources = info.get('sources', [])

    # Ensure there is at least one alias and one source, if empty, use None
    if not aliases:
        aliases = [skill_name]
    else:
        aliases.append(skill_name)
    if not sources:
        sources = [{}]

    for alias in aliases:
        for source in sources:
            skill = Skill(
                id = str(id_counter),
                skill = alias,
                display_name = source.get('displayName'),
                shortDescription = source.get('shortDescription'),
                longDescription = source.get('longDescription'),
            )

            id_counter += 1
            
            list_of_skills.append(skill)

logger.info(f"Number of skills processed: {id_counter}")

# Initialize the DB
logger.info('Initialize CosmosDB instance')
cosmosdb = CosmosDB_Utils()
# # cosmosdb.drop_db_collection("skill")
cosmosdb.collection = cosmosdb.db.skill

# Bulk Insertion
logger.info('Loading skills data into CosmosDB')
cosmosdb.bulk_upsert_data(list_of_skills)


# Vectorize and store embeddings in each document
# Initialize the vector store utils
vector_store = VectorStore_Utils()

# Create vector field for each document
vector_store.add_collection_content_vector_field("skill", cosmosdb.db)

# Create vector index for collection
vector_store.create_vector_index("skill", cosmosdb.db)
