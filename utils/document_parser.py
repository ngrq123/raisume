import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from dotenv import load_dotenv


def get_document_contents(file):
    load_dotenv()
    endpoint = os.getenv('DOCUMENTINTELLIGENCE_ENDPOINT')
    key = os.getenv('DOCUMENTINTELLIGENCE_API_KEY')

    # Reference: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", analyze_request=file, content_type="application/octet-stream")
    
    result: AnalyzeResult = poller.result()

    paragraphs = []
    for paragraph in result.paragraphs:
        if paragraph.role == 'sectionHeading':
            paragraphs.append('')
        paragraphs.append(paragraph.content)
    content = '\n'.join(paragraphs)

    return content

