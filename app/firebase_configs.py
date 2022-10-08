import pyrebase
import firebase_admin
from firebase_admin import credentials
import json
from dotenv import load_dotenv
import os

load_dotenv()

if (os.getenv("FIREBASE_KEY")):
    f = open("firebasekey2.json", "w")
    f.write(json.loads(os.getenv("FIREBASE_KEY")))
    f.close()

cred = credentials.Certificate("firebasekey2.json")

firebase = firebase_admin.initialize_app(cred)

firebaseConfig = {
    "apiKey": "AIzaSyD91WTkhydpLbHkBqTUvvnXXcybpjF7uL8",
    "authDomain": "fiuber-363101.firebaseapp.com",
    "projectId": "fiuber-363101",
    "storageBucket": "fiuber-363101.appspot.com",
    "messagingSenderId": "241358240016",
    "appId": "1:241358240016:web:877f17f6fbe238f54f8d95",
    "measurementId": "G-BKBJ28KEVW"
  };

pb = pyrebase.initialize_app(firebaseConfig)


def get_pb():
    return pb


def get_firebase():
    return firebase


def get_firebaseconfig():
    return firebaseConfig
