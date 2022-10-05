from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from ..schemas.voyage import InitVoyageBase, DriverBase
from ..database.mongo import db
from ..crud import clients, drivers
from ..firebase_notif.firebase import notify_drivers


router = APIRouter(
    prefix="/voyage",
    tags=['Voyage']
)




@router.post('/user')
def init_voyage(voyage: InitVoyageBase):
    """
    Client Search For A Driver
    """
    try: 
        clients.create_client(db, voyage)
        location_searched = [voyage.init.longitude, voyage.init.latitude]
        near_drivers = drivers.get_nearest_drivers(db, location_searched)
        notify_drivers(near_drivers, voyage)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error adding the client. '
            + str(err)},
            status_code=400)


@router.post('/driver')
def find_voyage(driver: DriverBase):
    """
    Driver Added To Waiting List
    """
    try:
        drivers.create_driver(db, driver)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the clients database '
            + str(err)},
            status_code=400)
    near_clients = clients.get_nearest_clients(db, driver)
    # notify_driver(near_clients, driver)



@router.delete('/user')
def cancel_voyage(voyage: InitVoyageBase):
    """
    Client Cancels Voyage Search
    """
    clients.delete(db, voyage)




# def start_voyage():
    # Sacar usuario de base de datos
    # Asignar viaje
