from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)

# Access database
nodb = client["your_database_name"]
