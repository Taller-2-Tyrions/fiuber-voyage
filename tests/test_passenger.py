import mongomock
from app.schemas import voyage, common
from app.schemas.voyage import PassengerStatus
from app.crud import passenger


def test_create_passenger():
    db = mongomock.MongoClient().db
    passenger_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=passenger_id, location=location,
                                  status=PassengerStatus.WAITING_DRIVER)

    passenger.create_passenger(db, person)

    user_found = passenger.find_passenger(db, passenger_id)

    assert (user_found.get("id") == passenger_id)
