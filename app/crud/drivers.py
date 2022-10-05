from fastapi.encoders import jsonable_encoder

# gateway ->users: create driver
# gateway -> voyage: create driver -> agregamos Id y ubicacion actual a bdd.
# (BDD Driver) -> ubicacion, id.
# le mandamos a todos los que estan cerca de esta ubicacion.

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

def get_nearest_drivers(db, voyage):
    # nearest = db.drivers.aggregate([
    #     {"$match": {"is_searching": {"$eq": True}}},
    #     {"$near": {
    #         "$geometry": {
    #             "type": "Point",
    #             "coordinates": voyage.init
    #         },
    #     }},
    #     {"$limit": MAX_DRIVERS_FOUND}
    # ])
    nearest = db.drivers.aggregate([
        {"$match": {"is_searching": {"$eq": True}}},
        {"$geoNear": {
            "near": voyage.init,
            "distanceField": "distance"
        }},
        {"$limit": MAX_DRIVERS_FOUND}
    ])
    return nearest
