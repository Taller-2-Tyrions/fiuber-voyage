import mongomock
from app.schemas import voyage, common
from app.schemas.voyage import PassengerStatus
from app.crud import passenger
from time import sleep
import datetime


def test_create_client():
    db = mongomock.MongoClient().db
    client_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=client_id, location=location, status=PassengerStatus.WAITING_DRIVER)
    user_example = voyage.InitVoyageBase(passenger=person, init=location,
                                         end=location)
    passenger.create_client(db, user_example)

    user_found = passenger.find_client(db, client_id)

    passenger0 = user_found.get("passenger")

    assert (passenger0.get("id") == client_id)


def test_expire_client():
    db = mongomock.MongoClient().db
    client_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=client_id, location=location, status=PassengerStatus.WAITING_DRIVER)
    user_example = voyage.InitVoyageBase(passenger=person, init=location,
                                         end=location)
    passenger.create_client(db, user_example, 1)

    sleep(3)
    print(datetime.datetime.now())

    user_found = passenger.find_client(db, client_id)

    assert (user_found is None)
