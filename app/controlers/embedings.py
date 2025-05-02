import openai
from dotenv import load_dotenv
import os


env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")
openai.api_key = os.getenv("API_KEY")

def generate_embeddings(chunks):
    embedding_documents = []
    for chunk in chunks:
        response =  openai.embeddings.create(
            model="text-embedding-ada-002",
            input=chunk
        )
        embedding = response.data[0].embedding
        embedding_documents.append({
            "text": chunk,
            "embedding_table": embedding
        })
    return embedding_documents