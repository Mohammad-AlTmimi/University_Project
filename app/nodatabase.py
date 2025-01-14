from pymongo import MongoClient


# MongoDB URI
MONGO_URI = "mongodb://localhost:27017"

# Create a MongoClient instance (this will establish the connection)
client = MongoClient(MONGO_URI)

# Access the database
nodb = client["HebronChatGBT"]
# collection === table
def get_nodb() -> dict:
    """
    Returns the MongoDB database object for dependency injection in FastAPI.
    """
    return nodb
