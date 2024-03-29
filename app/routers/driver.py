import requests
import os
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from app.schemas.common import Point
from ..schemas.voyage import DriverBase, PassengerStatus, VoyageStatus
from ..schemas.voyage import DriverStatus
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..firebase_notif import firebase as notifications


router = APIRouter(
    prefix="/voyage/driver",
    tags=['Voyage Driver']
)

CLOSE_METERS = 100

GOOGLE_MAPS_URL = os.getenv("GOOGLE_MAPS_URL")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def is_status_correct(status_code):
    return status_code//100 == 2


def distance_to(_origin_point, _dest_point):
    origin_point = str(_origin_point.latitude)+','+str(_origin_point.longitude)
    dest_point = str(_dest_point.latitude)+','+str(_dest_point.longitude)

    url = GOOGLE_MAPS_URL+"?origins=" + origin_point + "&destinations="
    url += dest_point + "&unit=km;key=" + GOOGLE_MAPS_API_KEY
    resp = requests.get(GOOGLE_MAPS_URL+"?origins=" + origin_point +
                        "&destinations=" + dest_point +
                        "&unit=km&key=" + GOOGLE_MAPS_API_KEY)

    if (not is_status_correct(resp.status_code)):
        raise HTTPException(detail={
                    'message': resp.reason
                }, status_code=500)

    resp_json = resp.json()

    if resp_json['rows'][0]['elements'][0].get("status") == 'ZERO_RESULTS':
        raise Exception("Path Not Found In Google Maps. "
                        "Make sure these are valid points")

    distance_in_mts = resp_json['rows'][0]['elements'][0]['distance']['value']

    return distance_in_mts


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
    A Searching/Waiting driver is set to Offline
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
    driver = drivers.find_driver(db, driver_id)

    if driver.get("status") == DriverStatus.GOING.value:
        id_voyage = voyages.get_current_voyage(db, driver_id,
                                               is_driver=True)
        voyage = voyages.find_voyage(db, id_voyage)
        voy_status = voyage.get("status")

        if voy_status == VoyageStatus.STARTING.value:
            init = voyage.get("init")
            start = Point(latitude=init.get("latitude"),
                          longitude=init.get("longitude"))
            distance = distance_to(location, start)

            if distance < CLOSE_METERS:
                voyages.set_arriving_status(db, id_voyage)

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
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)

    driver_registered = voyage.get("driver_id")
    if driver_registered != driver_id:
        raise HTTPException(detail={'message': 'Not Your Voyage'},
                            status_code=400)

    passenger_id = voyage.get("passenger_id")
    try:
        voyage_status = voyage.get("status")

        reset = True

        if status and voyage_status == VoyageStatus.WAITING.value:
            passenger.set_waiting_driver_status(db, passenger_id)
            drivers.set_going_status(db, driver_id)
            voyages.set_starting_status(db, id_voyage)
            notifications.notify_driver_accepted(passenger_id, voyage)
        elif not status or voyage_status == VoyageStatus.STOPPED.value:
            voyages.delete_voyage(db, id_voyage)
            passenger.change_status(db, passenger_id,
                                    PassengerStatus.CHOOSING.value)
            drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
            if VoyageStatus.WAITING.value:
                notifications.notify_driver_declined(passenger_id, voyage)
        else:
            reset = False
            raise Exception('Already Going Voyage')
    except Exception as err:
        if reset:
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
