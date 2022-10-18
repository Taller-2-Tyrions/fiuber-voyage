import pyrebase
import firebase_admin
from firebase_admin import credentials
import json
from dotenv import load_dotenv
import os

load_dotenv()


def load_firebase():

    if (os.getenv("FIREBASE_KEY")):
        f = open("firebasekey.json", "w")
        f.write(json.loads(os.getenv("FIREBASE_KEY")))
        f.close()

    cred = credentials.Certificate("firebasekey.json")

    firebase_admin.initialize_app(cred, {
            'databaseURL': "https://fiuber-36b86-default-rtdb.firebaseio.com/"
    })
    firebaseConfig = {
        "apiKey": "AIzaSyBSenFicB4rNCqRO183gmoMILDImbTR84Y",
        "authDomain": "fiuber-36b86.firebaseapp.com",
        "projectId": "fiuber-36b86",
        "storageBucket": "fiuber-36b86.appspot.com",
        "messagingSenderId": "388259755156",
        "appId": "1:388259755156:web:04d82df1a410135ee9f081",
        'databaseURL': "https://fiuber-36b86-default-rtdb.firebaseio.com/"
    }

    pyrebase.initialize_app(firebaseConfig)
