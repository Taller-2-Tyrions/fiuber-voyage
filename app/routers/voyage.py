from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..schemas.voyage import PassengerStatus, ReviewBase
from ..schemas.voyage import DriverStatus, VoyageStatus
from ..database.mongo import db
from ..crud import drivers, passenger, voyages

router = APIRouter(
    prefix="/voyage",
    tags=['Voyage']
)


@router.delete('/{voyage_id}/{caller_id}')
def cancel_confirmed_voyage(voyage_id: str, caller_id: str):
    """
    Driver or Passenger Cancel Voyage Previously Confirmed.
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
        raise HTTPException(detail={'message': "Can't Cancel Others Voyage"},
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

    voyages.change_status(db, voyage_id, VoyageStatus.CANCELLED.value)


@router.get('/last/{user_id}/{is_driver}')
def get_last_voyages(user_id: str, is_driver: bool):
    """
    Get the last 5 voyages for the user
    """
    try:
        return voyages.get_last_voyages(db, user_id, is_driver)
    except Exception:
        raise HTTPException(detail={'message': "Can't Access Database"},
                            status_code=400)


@router.post('/review/{voyage_id}/{caller_id}')
def add_review(voyage_id: str,  caller_id: str, review: ReviewBase):
    """
    User Load A Review Of Voyage
    """
    voyage = voyages.find_voyage(db, voyage_id)
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)

    searched_id = "passenger_id"
    if review.by_driver:
        searched_id = "driver_id"

    saved_id = voyage.get(searched_id)
    if caller_id != saved_id:
        raise HTTPException(detail={'message': 'User Not In Voyage Asked'},
                            status_code=400)

    voyages.add_review(db, voyage_id, review)
