import mongomock
from app.schemas import voyage, common
from app.schemas.voyage import PassengerStatus
from app.crud import passenger


def test_create_client():
    db = mongomock.MongoClient().db
    client_id = "10"
    location = common.Point(longitude=50, latitude=50)
    person = voyage.PassengerBase(id=client_id, location=location,
                                  status=PassengerStatus.WAITING_DRIVER)

    passenger.create_passenger(db, person)

    user_found = passenger.find_passenger(db, client_id)

    assert (user_found.get("id") == client_id)
