import mongomock
from datetime import datetime, timedelta
from app.schemas import common, voyage
from app.schemas.voyage import ComplaintBase, ReviewBase, VoyageBase
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

    voyage_found = voyages.find_voyage(db, id)

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

    voyages.set_starting_status(db, id)

    voyage_found = voyages.find_voyage(db, id)

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
        voyages.set_finished_status(db, id)


def test_get_day_voyages():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    driver_id = "10"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)

    for i in range(0, 50):
        time = datetime.utcnow()
        time = time - timedelta(hours=i)
        time = time + timedelta(minutes=1)
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
    assert (voyages_passenger == 25)

    voyages_driver = voyages.get_date_voyages(db, driver_id,
                                              is_driver=True,
                                              is_daily=True)
    assert (voyages_driver == 25)


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


def test_push_review():
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

    review = ReviewBase(score=4, by_driver=True, comment="Todo Muy Lindo")

    voyages.add_review(db, id, review)

    voyage_found = voyages.find_voyage(db, id)

    reviews = voyage_found.get("reviews")

    assert (len(reviews) == 1)
    assert (reviews[0].get("score") == 4)


def test_push_complaint():
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

    comp_type = voyage.ComplaintType.AGGRESIVE.value

    complaint = ComplaintBase(complaint_type=comp_type,
                              description="Grito Todo El Viaje Por Un Partido")

    voyages.add_complaint(db, id, complaint)

    voyage_found = voyages.find_voyage(db, id)

    complaints = voyage_found.get("complaints")

    assert (len(complaints) == 1)
    assert (complaints[0].get("complaint_type") == comp_type)


def test_get_average():
    db = mongomock.MongoClient().db
    passenger_id = "19"
    location_init = common.Point(longitude=50, latitude=50)
    location_end = common.Point(longitude=51, latitude=50.4)

    today = datetime.utcnow()

    for i in range(0, 3):
        driver_id = str(i)
        voyage_test = VoyageBase(passenger_id=passenger_id,
                                 driver_id=driver_id,
                                 init=location_init,
                                 end=location_end,
                                 status=voyage.VoyageStatus.FINISHED.value,
                                 price=10, start_time=today,
                                 end_time=datetime.utcnow(), is_vip=True)
        id = voyages.create_voyage(db, voyage_test)
        review = ReviewBase(score=3, by_driver=True,
                            comment="Todo Muy Lindo")
        voyages.add_review(db, id, review)
        review = ReviewBase(score=0, by_driver=False,
                            comment="Muy Mala Onda")
        voyages.add_review(db, id, review)

    passenger_avg = voyages.get_average_score(db, passenger_id,
                                              is_driver=False)
    assert (passenger_avg == 3)

    passenger_avg = voyages.get_average_score(db, driver_id,
                                              is_driver=True)
    assert (passenger_avg == 0)
