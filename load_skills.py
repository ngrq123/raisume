import pandas as pd
import json


from models.skills import Skill
from db_utils import CosmosDB_Utils

# Load in the skills
with open('./assets/skills.json') as f:
    skill_dict = json.load(f)

# Process the skills dictionary
list_of_skills = []
id_counter = 0
for skill_name, info in skill_dict.items():
    aliases = info.get('aliases', [])
    sources = info.get('sources', [])

    # Ensure there is at least one alias and one source, if empty, use None
    if not aliases:
        aliases = None
    if not sources:
        sources = [{}]

    for source in sources:
        skill = Skill(
            id = str(id_counter),
            skill = skill_name,
            aliases = aliases,
            source_id = source.get('id'),
            display_name = source.get('displayName'),
            shortDescription = source.get('shortDescription'),
            longDescription = source.get('longDescription'),
            url = source.get('url')
        )

        list_of_skills.append(skill)
        
        id_counter += 1

# Initialize the DB
cosmosdb = CosmosDB_Utils()
cosmosdb.collection = cosmosdb.db.skill

# # Bulk Insertion
cosmosdb.bulk_upsert_data(list_of_skills)
