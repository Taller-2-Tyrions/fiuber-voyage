from pymongo import MongoClient, GEOSPHERE
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, 8000)
db = client["voyages"]

clients = db.clients
drivers = db.drivers

clients.create_index([("init", GEOSPHERE)])
#clients.create_index([("expireAt", 1), ("expireAfterSeconds", 0)])
drivers.create_index([("location", GEOSPHERE)])
