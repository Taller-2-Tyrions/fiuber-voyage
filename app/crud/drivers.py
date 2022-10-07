from fastapi.encoders import jsonable_encoder
from ..schemas.voyage import DriverStatus
from fastapi.exceptions import HTTPException

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


def delete_driver(db, driver_id):
    db["drivers"].find_one_and_delete({"id": driver_id})


def get_nearest_drivers(db, location):
    nearest = db.drivers.aggregate([
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": location},
            "distanceField": "dist.calculated"
        }},
        {"$match": {"status": {"$eq": DriverStatus.SEARCHING}}},
        {"$limit": MAX_DRIVERS_FOUND}
    ])
    return nearest


def update_driver(db, driver_id: str, changes):
    changes = jsonable_encoder(changes)
    driver_found = db["drivers"].find_one_and_update({"id": driver_id},
                                                    {"$set": changes})
    return set_return_value(driver_found)


def set_waiting_if_searching(db, driver_id):
    driver_status = find_driver(db, driver_id).get("status")
    if driver_status != DriverStatus.SEARCHING:
        raise HTTPException(detail={
            'message': 'Driver is not available.'},
            status_code=400)
    change_status(db, driver_id, DriverStatus.WAITING)
