from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
import datetime
SECONDS_LIMIT = 60*10

# user -> solicita viaje
# lista de choferes disp
# elige chofer de la lista
# ahi chofer acepta o rechaza

def create_client(db, voyage, limit = SECONDS_LIMIT):
    user_encoded = jsonable_encoder(voyage)
    actual_time = datetime.datetime.now() 
    expire_time = actual_time + datetime.timedelta(seconds = limit)
    print(expire_time)
    user_encoded.update({"expireAfterSeconds": limit})
    db["clients"].insert_one(user_encoded)

    
    
def find_client(db, client_id):
    return db["clients"].find_one({"passenger.id": client_id}, {"_id": 0})