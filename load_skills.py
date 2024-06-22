import pandas as pd
import json
import logging

from models.skills import Skill
from db_utils import CosmosDB_Utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load in the skills
with open('./assets/skills.json') as f:
    skill_dict = json.load(f)
logger.info('Skills JSON loaded into Python. Processing...')
print(len(skill_dict))
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
cosmosdb.collection = cosmosdb.db.skill

# Bulk Insertion
logger.info('Loading skills data into CosmosDB')
cosmosdb.bulk_upsert_data(list_of_skills)
