from pymongo import MongoClient, GEOSPHERE
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, 8000)
db = client["voyages"]

clients = db.passenger
drivers = db.drivers
voyage = db.voyage

clients.create_index([("init", GEOSPHERE)])
drivers.create_index([("location", GEOSPHERE)])
