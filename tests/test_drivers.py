import mongomock
from app.schemas import voyage, common
from app.crud import drivers
import pymongo
import pytest

test_client = pymongo.MongoClient()
db_testing = test_client["mydatabase"]


def test_create_driver():
    db = mongomock.MongoClient().db
    driver_id = "10"
    location = common.Point(longitude=50, latitude=50)
    driver_example = voyage.DriverBase(id=driver_id, location=location,
                                       status=voyage.DriverStatus.GOING,
                                       is_vip=False)
    drivers.create_driver(db, driver_example)

    user_found = drivers.find_driver(db, driver_id)

    assert (user_found.get("id") == driver_id)


def test_change_driver_searching_status():
    db = mongomock.MongoClient().db
    driver_id = "10"
    offline = voyage.DriverStatus.OFFLINE.value
    location = common.Point(longitude=50, latitude=50)
    driver_example = voyage.DriverBase(id=driver_id, location=location,
                                       status=offline,
                                       is_vip=False)
    drivers.create_driver(db, driver_example)

    user_found = drivers.find_driver(db, driver_id)
    assert (user_found.get("status") == voyage.DriverStatus.OFFLINE.value)

    drivers.change_status(db, driver_id, voyage.DriverStatus.GOING.value)
    user_found = drivers.find_driver(db, driver_id)
    assert (user_found.get("status") == voyage.DriverStatus.GOING.value)


def test_change_waiting_confirmation_status():
    db = mongomock.MongoClient().db
    driver_id = "10"
    location = common.Point(longitude=50, latitude=50)
    driver = voyage.DriverBase(id=driver_id, location=location,
                               status=voyage.DriverStatus.SEARCHING.value,
                               is_vip=False)

    drivers.create_driver(db, driver)
    drivers.set_waiting_status(db, driver_id)

    user_found = drivers.find_driver(db, driver_id)

    waiting = voyage.DriverStatus.WAITING.value

    assert (user_found.get("status") == waiting)


def test_change_waiting_confirmation_status_should_raise():
    db = mongomock.MongoClient().db
    driver_id = "10"
    location = common.Point(longitude=50, latitude=50)
    driver = voyage.DriverBase(id=driver_id, location=location,
                               status=voyage.DriverStatus.TRAVELLING.value,
                               is_vip=False)

    drivers.create_driver(db, driver)

    with pytest.raises(Exception):
        drivers.set_waiting_status(db, driver_id)


def test_update_driver():
    db = mongomock.MongoClient().db
    driver_id = "10"
    offline = voyage.DriverStatus.OFFLINE.value
    location = common.Point(longitude=50, latitude=50)
    driver_example = voyage.DriverBase(id=driver_id, location=location,
                                       status=offline,
                                       is_vip=False)
    drivers.create_driver(db, driver_example)

    user_found = drivers.find_driver(db, driver_id)
    assert (not user_found.get("is_vip"))

    drivers.update_driver(db, driver_id, {"is_vip": True})
    user_found = drivers.find_driver(db, driver_id)
    assert (user_found.get("is_vip"))


# TODO: Falta testear get Nearest Drivers, pero porque
# solo se corre en compus con cierta config de mongo.

# def test_create_in_mongo_localhost():
#     driver_id = "10"
#     location = common.Point(longitude=50, latitude=50)
#     driver_example = voyage.DriverBase(id=driver_id, location=location,
#                                      status=voyage.DriverStatus.GOING,
#                                      is_vip=False)
#     drivers.create_driver(db_testing, driver_example)

#     user_found = drivers.find_driver(db_testing, driver_id)

#     assert (user_found.get("id") == driver_id)


# def test_nearest_drivers():
#     drivers_collection = db_testing.drivers

#     drivers_collection.create_index([("location", pymongo.GEOSPHERE)])

#     drivers_collection.delete_many({})

#     for i in range(50):
#         driver_id = str(i)
#         is_searching = i % 2 == 0
#         location = common.Point(longitude=i, latitude=i)
#         driver_example = voyage.DriverBase(id=driver_id, location=location,
#                                   is_searching=is_searching, is_vip=False)
#         drivers.create_driver(db_testing, driver_example)

#     print("Los Chofered Se Añadieron")

#     location_searched = [0, 0]
#     nearest = drivers.get_nearest_drivers(db_testing, location_searched)

#     ids = []

#     for driver in nearest:
#         print(driver)
#         ids.append(driver.get("id"))

#     for i in range(50):
#         if i < drivers.MAX_DRIVERS_FOUND*2 and i % 2 == 0:
#             assert (str(i) in ids)
#         else:
#             assert (str(i) not in ids)

#     drivers_collection.delete_many({})
