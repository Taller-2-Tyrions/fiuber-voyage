from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from app.schemas.common import Point
from ..schemas.voyage import SearchVoyageBase, DriverBase, PassengerStatus
from ..schemas.voyage import DriverStatus, VoyageBase, VoyageStatus
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..prices import pricing

router = APIRouter(
    prefix="/voyage",
    tags=['Voyage']
)


@router.post('/user')
def init_voyage(voyage: SearchVoyageBase):
    """
    Client Search For All Nearest Drivers
    """
    try:
        location_searched = [voyage.init.longitude, voyage.init.latitude]
        near_drivers = drivers.get_nearest_drivers(db, location_searched)
        prices = pricing.get_voyage_info(voyage, near_drivers)
        passenger.create_passenger(db, voyage.passenger)

        return prices
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error adding the client. '
            + str(err)},
            status_code=400)


# TODO: Agregar al SearchVoyageBase calificacion de user, etc.
@router.post('/user/{id_driver}')
def ask_for_voyage(id_driver: str, voyage: SearchVoyageBase):
    """
    Client Chose a Driver.
    """
    try:
        driver = drivers.find_driver(db, id_driver)
        price = pricing.price_voyage(voyage, driver)

        confirmed_voyage = VoyageBase(passenger_id=voyage.passenger.id,
                                      driver_id=id_driver, init=voyage.init,
                                      end=voyage.end,
                                      status=VoyageStatus.WAITING.value,
                                      price=price)

        id = voyages.create_voyage(db, confirmed_voyage)
        drivers.set_waiting_status(db, id_driver)
        passenger.set_waiting_confirmation_status(db, voyage.passenger.id)

        # send push notif to driver

        return {"final_price": price, "voyage_id": str(id), "message":
                "Waiting for Drivers answer."}

    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error adding the client. '
            + str(err)},
            status_code=400)


@router.post('/driver')
def add_driver(driver: DriverBase):
    """
    Add Driver To Searching List
    """
    try:
        drivers.create_driver(db, driver)
        drivers.change_status(db, driver.id, DriverStatus.SEARCHING.value)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the drivers database '
            + str(err)},
            status_code=400)


@router.post('/driver/{id_voyage}/{status}')
def accept_voyage(id_voyage: str, status: bool, driver_id: str):
    """
    Driver Acepts (True) / Declines (False) client solicitation
    """

    voyage = voyages.find_voyage(db, id_voyage)
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)
    try:
        if status:
            passenger.set_waiting_driver_status(db, voyage.get("passenger_id"))
            drivers.set_going_status(db, driver_id)
            voyages.set_starting_status(db, id_voyage)
            # push notification
        else:
            voyages.delete_voyage(db, id_voyage)
            passenger.change_status(db, voyage.get("passenger_id"),
                                    PassengerStatus.CHOOSING.value)
            drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
            # push notif al passenger
    except Exception as err:
        raise HTTPException(detail={'message': 'There was an error ... '
                            + str(err)},
                            status_code=400)


@router.delete('/voyage_search')
def cancel_search(passenger_id: str):
    """
    Client Cancels Voyage Search
    """
    passenger.change_status(db, passenger_id, PassengerStatus.CHOOSING.value)


@router.delete('/voyage/{voyage_id}/{caller_id}')
def cancel_confirmed_voyage(voyage_id: str, caller_id: str):
    """
    Cancel Voyage Previously Confirmed By Client
    """
    voyage = voyages.find_voyage(db, voyage_id)
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)
    voyage_status = voyage.get("status")
    passenger_id = voyage.get("passenger_id")
    driver_id = voyage.get("driver_id")

    is_passenger = caller_id == passenger_id
    is_driver = caller_id == driver_id

    if not is_driver and not is_passenger:
        raise HTTPException(detail={'message': "You Can't Cancel Others"},
                            status_code=400)

    if voyage_status == VoyageStatus.WAITING.value and is_passenger:
        drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
        passenger.change_status(db, passenger_id,
                                PassengerStatus.CHOOSING.value)
    elif voyage_status == VoyageStatus.STARTING.value:
        drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
        passenger.change_status(db, passenger_id,
                                PassengerStatus.CHOOSING.value)
        if is_passenger:
            print("Multado")
            # TODO Cobrar Multa
            # Push Notification A Driver
        else:
            print("Beneficiado?")
            # TODO Devolver Plata?
            # Push Notification A User
    else:
        raise HTTPException(detail={'message': 'Non Cancellable Voyage '},
                            status_code=400)

    voyages.delete_voyage(db, voyage_id)


@router.post('/start/{voyage_id}/{caller_id}')
def inform_start_voyage(voyage_id: str, caller_id: str):
    """
    Inform Driver Arrived Initial Point
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


@router.post('/finish/{voyage_id}/{caller_id}')
def inform_finish_voyage(voyage_id: str, caller_id: str):
    """
    Inform Voyage Has Finished
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


@router.post('/start_search/{driver_id}')
def activate_driver(driver_id: str):
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


@router.post("/location/{driver_id}")
def locate_driver(driver_id: str, location: Point):
    """
    Recieves a driver id an update the location of it in the database
    """
    changes = {"location": location}
    return drivers.update_driver(db, driver_id, changes)


@router.post('/stop_search/{driver_id}')
def deactivate_driver(driver_id: str):
    """
    A Seaching driver is set to Offline
    """
    driver = drivers.find_driver(db, driver_id)
    if not driver:
        raise HTTPException(detail={'message': 'Non Existent Driver'},
                            status_code=400)

    status = driver.get("status")

    is_offline = status == DriverStatus.OFFLINE.value
    is_searching = status == DriverStatus.SEARCHING.value

    if not is_offline and not is_searching:
        raise HTTPException(detail={'message': "Can't Change To Offline"},
                            status_code=400)

    drivers.change_status(db, driver_id, DriverStatus.OFFLINE.value)
