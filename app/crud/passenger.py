from fastapi.encoders import jsonable_encoder
from ..schemas.voyage import PassengerStatus


def create_passenger(db, passenger):
    user_encoded = jsonable_encoder(passenger)
    db["passenger"].insert_one(user_encoded)


def find_passenger(db, passenger_id):
    return db["passenger"].find_one({"id": passenger_id}, {"_id": 0})


def change_status(db, passenger_id, state):
    changes = {"status": state}
    db["passenger"].find_one_and_update({"id": passenger_id},
                                        {"$set": changes})


def set_waiting_confirmation_status(db, passenger_id):
    passenger_status = find_passenger(db, passenger_id).get("status")
    if passenger_status != PassengerStatus.CHOOSING.value:
        raise Exception("Passenger is not available.")
    change_status(db, passenger_id, PassengerStatus.WAITING_CONFIRMATION.value)


def set_waiting_driver_status(db, passenger_id):
    passenger_status = find_passenger(db, passenger_id).get("status")
    if passenger_status != PassengerStatus.WAITING_CONFIRMATION.value:
        raise Exception("Passenger is not available.")
    change_status(db, passenger_id, PassengerStatus.WAITING_DRIVER.value)


def delete_passenger(db, passenger_id):
    db["passenger"].find_one_and_delete({"id": passenger_id})