from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://al062392:3Nt20yQLAn68TdkU@cluster0.76rmx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster 0"
client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.chat_db
messages_collection = db.messages