from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..schemas.voyage import PassengerStatus
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
