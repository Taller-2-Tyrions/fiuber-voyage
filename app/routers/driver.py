from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from app.schemas.common import Point
from ..schemas.voyage import DriverBase, PassengerStatus
from ..schemas.voyage import DriverStatus
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..firebase_notif import firebase as notifications


router = APIRouter(
    prefix="/voyage/driver",
    tags=['Voyage Driver']
)


@router.post('/signup/{id_driver}')
def add_driver(id_driver: str):
    """
    Add Driver To List
    """
    try:
        location = Point(longitude=50.0, latitude=50.0)
        driver = DriverBase(id=id_driver, location=location,
                            status=DriverStatus.OFFLINE.value,
                            is_vip=False)
        drivers.create_driver(db, driver)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the drivers database '
            + str(err)},
            status_code=400)


@router.post('/searching/{driver_id}')
def activate_driver(driver_id: str, location: Point):
    """
    An offline driver is set to searching
    """
    driver = drivers.find_driver(db, driver_id)
    if not driver:
        raise HTTPException(detail={'message': 'Non Existent Driver'},
                            status_code=400)

    status = driver.get("status")

    is_offline = status == DriverStatus.OFFLINE.value
    is_searching = status == DriverStatus.SEARCHING.value

    if not is_offline and not is_searching:
        raise HTTPException(detail={'message': "Can't Change To Searching"},
                            status_code=400)

    drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
    changes = {"location": location}
    return drivers.update_driver(db, driver_id, changes)


@router.post('/offline/{driver_id}')
def deactivate_driver(driver_id: str):
    """
    A Seaching driver is set to Offline
    """
    driver = drivers.find_driver(db, driver_id)
    if not driver:
        raise HTTPException(detail={'message': 'Non Existent Driver'},
                            status_code=400)

    status = driver.get("status")

    is_going = status == DriverStatus.GOING.value
    is_travelling = status == DriverStatus.TRAVELLING.value

    if is_going or is_travelling:
        raise HTTPException(detail={'message': "Can't Change To Offline"},
                            status_code=400)

    drivers.change_status(db, driver_id, DriverStatus.OFFLINE.value)


@router.post('/vip/{driver_id}/{is_vip}')
def driver_change_vip(driver_id: str, is_vip: bool):
    """
    Change VIP Status of Driver
    """
    try:
        changes = {"is_vip": is_vip}
        return drivers.update_driver(db, driver_id, changes)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the drivers database '
            + str(err)},
            status_code=400)


@router.post("/location/{driver_id}")
def locate_driver(driver_id: str, location: Point):
    """
    Recieves a driver id an update the location of it in the database
    """
    changes = {"location": location}
    return drivers.update_driver(db, driver_id, changes)


@router.get("/location/{driver_id}")
def get_loc(driver_id: str):
    return {"location": drivers.get_location(db, driver_id)}


@router.post('/reply/{id_voyage}/{status}/{driver_id}')
def accept_voyage(id_voyage: str, status: bool, driver_id: str):
    """
    Driver Acepts (True) / Declines (False) client solicitation
    """

    voyage = voyages.find_voyage(db, id_voyage)
    passenger_id = voyage.get("passenger_id")
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)
    try:
        if status:
            passenger.set_waiting_driver_status(db, passenger_id)
            drivers.set_going_status(db, driver_id)
            voyages.set_starting_status(db, id_voyage)
            notifications.notify_driver_accepted(passenger_id, voyage)
        else:
            voyages.delete_voyage(db, id_voyage)
            passenger.change_status(db, passenger_id,
                                    PassengerStatus.CHOOSING.value)
            drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
            notifications.notify_driver_declined(passenger_id, voyage)
    except Exception as err:
        passenger.change_status(db, passenger_id,
                                PassengerStatus.CHOOSING.value)
        drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
        voyages.delete_voyage(db, id_voyage)
        raise HTTPException(detail={'message': 'There was an error ... '
                            + str(err)},
                            status_code=400)


@router.post('/start/{voyage_id}/{caller_id}')
def inform_start_voyage(voyage_id: str, caller_id: str):
    """
    Driver Informs Arrived Initial Point
    """
    voyage = voyages.find_voyage(db, voyage_id)
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)
    passenger_id = voyage.get("passenger_id")
    driver_id = voyage.get("driver_id")

    if caller_id != driver_id:
        raise HTTPException(detail={'message': 'No Authorized'},
                            status_code=400)

    voyages.set_travelling_status(db, voyage_id)
    drivers.set_travelling_status(db, driver_id)
    passenger.set_travelling_status(db, passenger_id)
    notifications.notify_has_started(passenger_id)


@router.post('/end/{voyage_id}/{caller_id}')
def inform_finish_voyage(voyage_id: str, caller_id: str):
    """
    Driver Informs Voyage Has Finished
    """
    voyage = voyages.find_voyage(db, voyage_id)
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)
    passenger_id = voyage.get("passenger_id")
    driver_id = voyage.get("driver_id")

    if caller_id != driver_id:
        raise HTTPException(detail={'message': 'No Authorized'},
                            status_code=400)

    voyages.set_finished_status(db, voyage_id)
    drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
    passenger.change_status(db, passenger_id, PassengerStatus.CHOOSING.value)
    notifications.notify_has_finished(passenger_id)
