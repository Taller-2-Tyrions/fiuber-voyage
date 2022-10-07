from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from ..schemas.voyage import InitVoyageBase, DriverBase
from ..database.mongo import db
from ..crud import drivers, passenger
from ..firebase_notif.firebase import notify_drivers
from prices import pricing

router = APIRouter(
    prefix="/voyage",
    tags=['Voyage']
)


@router.post('/user')
def init_voyage(voyage: InitVoyageBase):
    """
    Client Search For All Nearest Drivers
    """
    try:
        location_searched = [voyage.init.longitude, voyage.init.latitude]
        near_drivers = drivers.get_nearest_drivers(db, location_searched)
        return pricing.get_voyage_info(voyage, near_drivers)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error adding the client. '
            + str(err)},
            status_code=400)


# TODO: Agregar al InitVoyageBase calificacion de user, etc. 
@router.post('/user/{id_driver}')
def ask_for_voyage(id_driver: str, voyage: InitVoyageBase):
    """
    Client Chose a Driver. 
    """
    try:
        drivers.set_waiting_if_searching(db, id_driver):
        passenger.set_ 
            driver = drivers.find_driver(db, id_driver)
            voyage_info = pricing.get_voyage_info(voyage, [driver])
            
        # voyage_info = load_waiting_driver_voyage(voyage_info)
        #        Agregar en otra db que el cliente le pidio a este driver.
        #        el metodo de arriba tiene casos de error:
        #               2) el pasajero ya le pidio a otro driver por un viaje.
        # send_push_notif(voyage_info, id_driver)
        # Chofer pasa a estado "en espera" para que no pueda recibir nuevas solicitudes
        # return {"message": "Waiting for Drivers answer."}

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
        # hay que hacer que el chofer este activo en la aplicacion (esta buscando viaje)
        drivers.create_driver(db, driver)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the drivers database '
            + str(err)},
            status_code=400)




# un esquema que tenga id voyage y si lo acepta o lo rechaza. 
@router.post('/driver/{id_voyage}/{status}')
def find_voyage(driver: DriverBase):
    """
    Driver Acepts / Declines client solicitation
    """
    try:
        # if acepta viaje
        #    actualizar viaje con chofer yendo 
        #    push notification al pasajero con chofer yendo + info del viaje
        # else
        #    borramos el id del viaje de la base de datos. 
        #    push notif al pasajero con chofer no yendo. 
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error ... '
            + str(err)},
            status_code=400)






@router.delete('/user')
def cancel_voyage(voyage: InitVoyageBase):
    """
    Client Cancels Voyage Search
    """
    passenger.delete(db, voyage)




# def start_voyage():
    # Sacar usuario de base de datos
    # Asignar viaje
