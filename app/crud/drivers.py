from fastapi.encoders import jsonable_encoder

MAX_DRIVERS_FOUND = 10


def create_driver(db, driver):
    driver = jsonable_encoder(driver)
    db["drivers"].insert_one(driver)


def find_driver(db, driver_id):
    return db["drivers"].find_one({"id": driver_id}, {"_id": 0})


def change_searching(db, driver_id, state):
    changes = {"is_searching": state}
    db["drivers"].find_one_and_update({"id": driver_id}, {"$set": changes})

def delete_driver(db, driver_id):
    db["drivers"].find_one_and_delete({"id": driver_id})

def get_nearest_drivers(db, location):
    nearest = db.drivers.aggregate([
        {"$geoNear": {
            "near": { "type": "Point", "coordinates": location },
            "distanceField": "dist.calculated"
        }},
        {"$match": {"is_searching": {"$eq": True}}},
        {"$limit": MAX_DRIVERS_FOUND}
    ])
    return nearest
