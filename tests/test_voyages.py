import mongomock
from datetime import datetime, timedelta
from app.schemas import common, voyage
from app.schemas.voyage import VoyageBase
from app.crud import voyages
import pytest


def test_create_voyage():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    driver_id = "10"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)
    test_voyage = VoyageBase(passenger_id=passenger_id,
                             driver_id=driver_id, init=location_init,
                             end=location_end,
                             status=voyage.VoyageStatus.WAITING.value,
                             price=10, start_time=datetime.utcnow(),
                             end_time=datetime.utcnow(), is_vip=True)

    id = voyages.create_voyage(db, test_voyage)

    voyage_found = voyages.find_voyage(db, str(id))

    assert (voyage_found.get("passenger_id") == passenger_id)


def test_change_waiting_status():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    driver_id = "10"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)
    test_voyage = VoyageBase(passenger_id=passenger_id,
                             driver_id=driver_id, init=location_init,
                             end=location_end,
                             status=voyage.VoyageStatus.WAITING.value,
                             price=10, start_time=datetime.utcnow(),
                             end_time=datetime.utcnow(), is_vip=True)

    id = voyages.create_voyage(db, test_voyage)

    voyages.set_starting_status(db, str(id))

    voyage_found = voyages.find_voyage(db, str(id))

    starting = voyage.VoyageStatus.STARTING.value

    assert (voyage_found.get("status") == starting)


def test_change_finished_status_should_raise():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    driver_id = "10"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)
    test_voyage = VoyageBase(passenger_id=passenger_id,
                             driver_id=driver_id, init=location_init,
                             end=location_end,
                             status=voyage.VoyageStatus.WAITING.value,
                             price=10, start_time=datetime.utcnow(),
                             end_time=datetime.utcnow(), is_vip=True)

    id = voyages.create_voyage(db, test_voyage)

    with pytest.raises(Exception):
        voyages.set_finished_status(db, str(id))


def test_get_day_voyages():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    driver_id = "10"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)

    for i in range(0, 50):
        time = datetime.utcnow()
        time = time - timedelta(hours=i)
        voyage_test = VoyageBase(passenger_id=passenger_id,
                                 driver_id=driver_id,
                                 init=location_init,
                                 end=location_end,
                                 status=voyage.VoyageStatus.FINISHED.value,
                                 price=10, start_time=time,
                                 end_time=datetime.utcnow(), is_vip=True)
        voyages.create_voyage(db, voyage_test)

    voyages_passenger = voyages.get_date_voyages(db, passenger_id,
                                                 is_driver=False,
                                                 is_daily=True)
    assert (voyages_passenger == 24)

    voyages_driver = voyages.get_date_voyages(db, driver_id,
                                              is_driver=True,
                                              is_daily=True)
    assert (voyages_driver == 24)


def test_get_months_voyages():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    driver_id = "10"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)

    today = datetime.utcnow()
    day = today.day

    for i in range(0, 50):
        time = today - timedelta(days=i)
        voyage_test = VoyageBase(passenger_id=passenger_id,
                                 driver_id=driver_id,
                                 init=location_init,
                                 end=location_end,
                                 status=voyage.VoyageStatus.FINISHED.value,
                                 price=10, start_time=time,
                                 end_time=datetime.utcnow(), is_vip=True)
        voyages.create_voyage(db, voyage_test)

    voyages_passenger = voyages.get_date_voyages(db, passenger_id,
                                                 is_driver=False,
                                                 is_daily=False)
    assert (voyages_passenger == day)

    voyages_driver = voyages.get_date_voyages(db, driver_id,
                                              is_driver=True,
                                              is_daily=False)
    assert (voyages_driver == day)


def test_get_seniority():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)

    today = datetime.utcnow()

    for i in range(0, 50):
        driver_id = str(i)
        time = today - timedelta(days=i)
        voyage_test = VoyageBase(passenger_id=passenger_id,
                                 driver_id=driver_id,
                                 init=location_init,
                                 end=location_end,
                                 status=voyage.VoyageStatus.FINISHED.value,
                                 price=10, start_time=time,
                                 end_time=datetime.utcnow(), is_vip=True)
        voyages.create_voyage(db, voyage_test)

    seniority = voyages.get_seniority(db, passenger_id,
                                      is_driver=False)
    assert (seniority == 49)

    for i in range(0, 50):
        driver_id = str(i)
        time = today - timedelta(days=i)
        seniority = voyages.get_seniority(db, driver_id,
                                          is_driver=True)
        assert (seniority == i)
