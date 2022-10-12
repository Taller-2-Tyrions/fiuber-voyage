from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId

from app.schemas.voyage import VoyageStatus


def set_return_value(res):
    if res:
        return str(res)
    else:
        return None


def find_voyage(db, voyage_id):
    found = db["voyage"].find_one({"_id": ObjectId(voyage_id)}, {"_id": 0})
    return found


def create_voyage(db, voyage):
    voyage = jsonable_encoder(voyage)
    value = db["voyage"].insert_one(voyage)
    return value.inserted_id


def change_status(db, voyage_id, state):
    changes = {"status": state}
    db["voyage"].find_one_and_update({"_id": ObjectId(voyage_id)},
                                     {"$set": changes})


def change_status_possible(db, voyage_id, new, before):
    voyage_status = find_voyage(db, voyage_id).get("status")
    print(find_voyage(db, voyage_id))
    if voyage_status != before:
        raise Exception("Voyage is not available.")
    change_status(db, voyage_id, new)


def set_starting_status(db, voyage_id):
    new_status = VoyageStatus.STARTING.value
    before_status = VoyageStatus.WAITING.value
    change_status_possible(db, voyage_id, new_status, before_status)


def set_travelling_status(db, voyage_id):
    new_status = VoyageStatus.TRAVELLING.value
    before_status = VoyageStatus.STARTING.value
    change_status_possible(db, voyage_id, new_status, before_status)


def set_finished_status(db, voyage_id):
    new_status = VoyageStatus.FINISHED.value
    before_status = VoyageStatus.TRAVELLING.value
    change_status_possible(db, voyage_id, new_status, before_status)


def delete_voyage(db, voyage_id):
    db["voyage"].find_one_and_delete({"_id": ObjectId(voyage_id)})
