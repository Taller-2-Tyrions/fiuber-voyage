from fastapi.encoders import jsonable_encoder
from ..schemas.voyage import PassengerStatus
from pymongo import ReturnDocument


def set_return_value(res):
    if res:
        return str(res)
    else:
        return None


def create_passenger(db, passenger):
    user_encoded = jsonable_encoder(passenger)
    db["passenger"].insert_one(user_encoded)


def find_passenger(db, passenger_id):
    return db["passenger"].find_one({"id": passenger_id}, {"_id": 0})


def change_status(db, passenger_id, state):
    changes = {"status": state}
    db["passenger"].find_one_and_update({"id": passenger_id},
                                        {"$set": changes})


def change_status_possible(db, passenger_id, new, before):
    passenger_status = find_passenger(db, passenger_id).get("status")
    if passenger_status != before:
        raise Exception("Passenger is not available.")
    change_status(db, passenger_id, new)


def set_waiting_confirmation_status(db, passenger_id):
    new_status = PassengerStatus.WAITING_CONFIRMATION.value
    before_status = PassengerStatus.CHOOSING.value
    change_status_possible(db, passenger_id, new_status, before_status)


def set_waiting_driver_status(db, passenger_id):
    new_status = PassengerStatus.WAITING_DRIVER.value
    before_status = PassengerStatus.WAITING_CONFIRMATION.value
    change_status_possible(db, passenger_id, new_status, before_status)


def set_travelling_status(db, passenger_id):
    new_status = PassengerStatus.TRAVELLING.value
    before_status = PassengerStatus.WAITING_DRIVER.value
    change_status_possible(db, passenger_id, new_status, before_status)


def update_passenger(db, passenger_id: str, changes):
    changes = jsonable_encoder(changes)
    after = ReturnDocument.AFTER
    passenger_found = db.passenger.find_one_and_update({"id": passenger_id},
                                                       {"$set": changes},
                                                       return_document=after)
    return set_return_value(passenger_found)
