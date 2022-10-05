from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, 8000)
db = client["voyages"]

clients = db.clients
drivers = db.drivers

clients.createIndex({"init": "2dsphere"})
drivers.createIndex({"location": "2dsphere"})
