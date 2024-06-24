import json
import logging
from models.skills import Skill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Data_Utils():

    def __init__(self):
        pass

    def read_json(self, file_path):
        # Load in the skills
        with open(file_path) as f:
            data = json.load(f)
        return data

    
    def process_skill_dict(self, skill_dict):
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