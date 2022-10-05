import mongomock
from app.schemas import voyage, common
from app.crud import drivers
import pymongo

test_client = pymongo.MongoClient()
db_testing = test_client["mydatabase"]


def test_create_driver():
    db = mongomock.MongoClient().db
    driver_id = "10"
    is_searching = True
    location = common.Point(longitude=50, latitude=50)
    user_example = voyage.DriverBase(id=driver_id, location=location,
                                     is_searching=is_searching)
    drivers.create_driver(db, user_example)

    user_found = drivers.find_driver(db, driver_id)

    assert (user_found.get("id") == driver_id)


def test_change_driver_searching_status():
    db = mongomock.MongoClient().db
    driver_id = "10"
    is_searching = True
    location = common.Point(longitude=50, latitude=50)
    user_example = voyage.DriverBase(id=driver_id, location=location,
                                     is_searching=is_searching)
    drivers.create_driver(db, user_example)

    user_found = drivers.find_driver(db, driver_id)
    assert (user_found.get("is_searching"))

    drivers.change_searching(db, driver_id, False)
    user_found = drivers.find_driver(db, driver_id)
    assert (not user_found.get("is_searching"))


def test_delete_driver():
    db = mongomock.MongoClient().db
    driver_id = "10"
    is_searching = True
    location = common.Point(longitude=50, latitude=50)
    user_example = voyage.DriverBase(id=driver_id, location=location,
                                     is_searching=is_searching)
    drivers.create_driver(db, user_example)
    drivers.delete_driver(db, driver_id)

    user_found = drivers.find_driver(db, driver_id)

    assert (user_found is None)


def test_create_in_mongo_localhost():
    driver_id = "10"
    is_searching = True
    location = common.Point(longitude=50, latitude=50)
    user_example = voyage.DriverBase(id=driver_id, location=location,
                                     is_searching=is_searching)
    drivers.create_driver(db_testing, user_example)

    user_found = drivers.find_driver(db_testing, driver_id)

    assert (user_found.get("id") == driver_id)


# def test_nearest_drivers():
#     is_searching = True
#     for i in range(5):
#         drivers.delete_driver(db_testing, str(i))
    
#     for i in range(5):
#         driver_id = str(i)
#         location = common.Point(longitude=i, latitude=i)
#         user_example = voyage.DriverBase(id=driver_id, location=location,
#                                          is_searching=is_searching)
#         drivers.create_driver(db_testing, user_example)

#     print("Los Chofered Se Añadieron")

#     location_searched = common.Point(longitude=0, latitude=0)
#     passenger = voyage.PersonBase(id="pepe", name="pepe", last_name="pepe")
#     voyage_searched = voyage.InitVoyageBase(passenger=passenger,
#                                             init=location_searched,
#                                             end=location_searched)

#     nearest = drivers.get_nearest_drivers(db_testing, voyage_searched)

#     print(f"Nearest Founds{nearest}")

#     ids = []

#     for driver in nearest:
#         ids.append(driver.id)

#     for i in range(drivers.MAX_DRIVERS_FOUND):
#         assert (str(i) in ids)

#     for i in range(5):
#         drivers.delete_driver(db_testing, str(i))
