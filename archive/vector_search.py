import json
import logging
import sys

from db_utils import CosmosDB_Utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the DB
cosmosdb = CosmosDB_Utils()
cosmosdb.collection = cosmosdb.db.skill

# Vector Search
query = "What is data science?"
results = cosmosdb.vector_search("skill", query, num_results=4)

document_fields_to_print = [
    'id',
    'skill',
    'sourceDisplayName',
    'shortDescription',
    'longDescription',
]

for result in results:
    cosmosdb.print_vector_search_result(result, document_fields_to_print)

        