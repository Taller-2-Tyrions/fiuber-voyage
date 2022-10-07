from fastapi.encoders import jsonable_encoder


def create_passenger(db, passenger):
    user_encoded = jsonable_encoder(passenger)
    db["passenger"].insert_one(user_encoded)


def find_passenger(db, client_id):
    return db["passenger"].find_one({"passenger.id": client_id}, {"_id": 0})
