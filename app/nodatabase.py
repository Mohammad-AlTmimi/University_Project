from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# MongoDB URI
MONGO_URI = "mongodb://localhost:27017"

# Create an async MongoClient instance
client = AsyncIOMotorClient(MONGO_URI)

# Access the database asynchronously
nodb: AsyncIOMotorDatabase = client["HebronChatGBT"]

async def get_nodb() -> AsyncIOMotorDatabase:
    """
    Asynchronously returns the MongoDB database object for dependency injection in FastAPI.
    """
    return nodb

async def delete_nodb():
    """
    Asynchronously deletes all documents from the 'messages' collection in the HebronChatGBT database.
    """
    collection_name = "messages"
    collection = nodb[collection_name]  # Access the collection
    result = await collection.delete_many({})  # Delete all documents asynchronously
    return {"deleted_count": result.deleted_count}
