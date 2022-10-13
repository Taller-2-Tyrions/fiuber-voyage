import pyrebase
import firebase_admin
from firebase_admin import credentials
import json
from dotenv import load_dotenv
import os

load_dotenv()

if (os.getenv("FIREBASE_KEY")):
    f = open("firebasekey.json", "w")
    f.write(json.loads(os.getenv("FIREBASE_KEY")))
    f.close()

cred = credentials.Certificate("firebasekey.json")

firebase = firebase_admin.initialize_app(cred)

const firebaseConfig = {
  "apiKey": "AIzaSyDoyemHyy6YoDE7pagRDyWYa-g7BK1ozEA",
  "authDomain": "fiuber-36b86.firebaseapp.com",
  "projectId": "fiuber-36b86",
  "storageBucket": "fiuber-36b86.appspot.com",
  "messagingSenderId": "388259755156",
  "appId": "1:388259755156:web:8227d1dbe93508d2e9f081"
};

pb = pyrebase.initialize_app(firebaseConfig)


def get_pb():
    return pb


def get_firebase():
    return firebase


def get_firebaseconfig():
    return firebaseConfig
