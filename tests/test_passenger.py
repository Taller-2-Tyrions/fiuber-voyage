import mongomock
from app.schemas import voyage, common
from app.schemas.voyage import PassengerStatus
from app.crud import passenger
import pytest


def test_create_passenger():
    db = mongomock.MongoClient().db
    passenger_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=passenger_id, location=location,
                                  status=PassengerStatus.WAITING_DRIVER,
                                  is_vip=False)

    passenger.create_passenger(db, person)

    user_found = passenger.find_passenger(db, passenger_id)

    assert (user_found.get("id") == passenger_id)


def test_change_status():
    db = mongomock.MongoClient().db
    passenger_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=passenger_id, location=location,
                                  status=PassengerStatus.WAITING_DRIVER.value,
                                  is_vip=False)

    passenger.create_passenger(db, person)
    passenger.change_status(db, passenger_id, PassengerStatus.TRAVELLING.value)

    user_found = passenger.find_passenger(db, passenger_id)

    assert (user_found.get("status") == PassengerStatus.TRAVELLING.value)


def test_change_waiting_confirmation_status():
    db = mongomock.MongoClient().db
    passenger_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=passenger_id, location=location,
                                  status=PassengerStatus.CHOOSING.value,
                                  is_vip=False)

    passenger.create_passenger(db, person)
    passenger.set_waiting_confirmation_status(db, passenger_id)

    user_found = passenger.find_passenger(db, passenger_id)

    waiting = PassengerStatus.WAITING_CONFIRMATION.value

    assert (user_found.get("status") == waiting)


def test_change_waiting_confirmation_status_should_raise():
    db = mongomock.MongoClient().db
    passenger_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=passenger_id, location=location,
                                  status=PassengerStatus.TRAVELLING.value,
                                  is_vip=False)

    passenger.create_passenger(db, person)

    with pytest.raises(Exception):
        passenger.set_waiting_confirmation_status(db, passenger_id)
