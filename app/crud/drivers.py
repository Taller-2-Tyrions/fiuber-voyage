from fastapi.encoders import jsonable_encoder
from ..schemas.voyage import DriverStatus
from pymongo import ReturnDocument

MAX_DRIVERS_FOUND = 10


def set_return_value(res):
    if res:
        return str(res)
    else:
        return None


def create_driver(db, driver):
    driver = jsonable_encoder(driver)
    db["drivers"].insert_one(driver)


def find_driver(db, driver_id):
    return db["drivers"].find_one({"id": driver_id}, {"_id": 0})


def change_status(db, driver_id, state):
    changes = {"status": state}
    db["drivers"].find_one_and_update({"id": driver_id}, {"$set": changes})


def change_status_possible(db, driver_id, new, before):
    driver_status = find_driver(db, driver_id).get("status")
    if driver_status != before:
        raise Exception("Driver is not available.")
    change_status(db, driver_id, new)


def set_waiting_status(db, driver_id):
    new_status = DriverStatus.WAITING.value
    before_status = DriverStatus.SEARCHING.value
    change_status_possible(db, driver_id, new_status, before_status)


def set_going_status(db, driver_id):
    new_status = DriverStatus.GOING.value
    before_status = DriverStatus.WAITING.value
    change_status_possible(db, driver_id, new_status, before_status)


def set_travelling_status(db, driver_id):
    new_status = DriverStatus.TRAVELLING.value
    before_status = DriverStatus.GOING.value
    change_status_possible(db, driver_id, new_status, before_status)


def get_nearest_drivers(db, location):
    nearest = db.drivers.aggregate([
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": location},
            "distanceField": "dist.calculated"
        }},
        {"$match": {"status": {"$eq": DriverStatus.SEARCHING.value}}},
        {"$limit": MAX_DRIVERS_FOUND}
    ])
    return nearest


def get_nearest_drivers_vip(db, location):
    nearest = db.drivers.aggregate([
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": location},
            "distanceField": "dist.calculated"
        }},
        {"$match": {"status": {"$eq": DriverStatus.SEARCHING.value},
                    "is_vip": {"$eq": True}}},
        {"$limit": MAX_DRIVERS_FOUND}
    ])
    return nearest


def update_driver(db, driver_id: str, changes):
    changes = jsonable_encoder(changes)
    after = ReturnDocument.AFTER
    driver_found = db["drivers"].find_one_and_update({"id": driver_id},
                                                     {"$set": changes},
                                                     return_document=after)
    return set_return_value(driver_found)
