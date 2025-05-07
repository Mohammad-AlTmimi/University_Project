from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_ATLAS_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

async def create_text_search_index(collection):
    try:
        await collection.create_search_index({
            "name": "text_search",
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "text": {
                            "type": "string",
                            "analyzer": "lucene.standard"
                        }
                    }
                }
            }
        })
        print("Text search index created successfully.")
    except Exception as e:
        print(f"Error creating text search index: {e}")

async def create_vector_search_index(collection):
    try:
        await collection.create_search_index({
            "name": "vector_search",
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "embedding_table": {
                            "type": "knnVector",
                            "dimensions": 1536,
                            "similarity": "cosine"
                        }
                    }
                }
            }
        })
        print("Vector search index created successfully.")
    except Exception as e:
        print(f"Error creating vector search index: {e}")

async def get_atlas_db():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    return db
        
async def is_index_active(collection, index_name):
    indexes = await collection.list_search_indexes().to_list()
    for index in indexes:
        if index['name'] == index_name and index.get('status') == 'READY':
            return True
    return False

async def test_connection():
    uri = "mongodb://admin:mysecurepassword@mongo-atlas:27018/?directConnection=true&authSource=admin"
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    try:
        await client.server_info()  # Forces a connection
        print("✅ MongoDB connected successfully.")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
    finally:
        client.close()


