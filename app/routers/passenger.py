from datetime import datetime
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from ..schemas.voyage import PassengerBase, SearchVoyageBase, PassengerStatus
from ..schemas.voyage import VoyageBase, VoyageStatus
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..prices import pricing

router = APIRouter(
    prefix="/voyage/passenger",
    tags=['Voyage Passenger']
)


@router.post('/')
def add_passenger(passenger: PassengerBase):
    """
    Add Passenger To List
    """
    try:
        passenger.create_passenger(db, passenger)
        passenger.change_status(db, passenger.id,
                                PassengerStatus.CHOOSING.value)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error adding the passenger '
            + str(err)},
            status_code=400)


@router.post('/vip/{passenger_id}/{is_vip}')
def passenger_change_vip(passenger_id: str, is_vip: bool):
    """
    Change VIP Status of passenger
    """
    try:
        changes = {"is_vip": is_vip}
        passenger.update_passenger(db, passenger_id, changes)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the passengers database '
            + str(err)},
            status_code=400)


@router.post('/search')
def search_near_drivers(voyage: SearchVoyageBase):
    """
    Passenger Search For All Nearest Drivers
    """
    try:
        location_searched = [voyage.init.longitude, voyage.init.latitude]
        near_drivers = drivers.get_nearest_drivers(db, location_searched)
        vip_prices = {}
        if voyage.is_vip:
            vip_drivers = drivers.get_nearest_drivers_vip(db,
                                                          location_searched)
            vip_prices = pricing.get_voyage_info(voyage,
                                                 vip_drivers, True)

        prices = pricing.get_voyage_info(voyage, near_drivers, False)

        final_prices = {}

        for driver, price in prices.items:
            final_prices.update({driver: {"Standard": price}})

        for driver, price in vip_prices.items:
            before = final_prices.get(driver, {})
            before.update({"VIP": price})
            final_prices.update({driver: before})

        return final_prices
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error searching drivers'
            + str(err)},
            status_code=400)


# TODO: Agregar al SearchVoyageBase calificacion de user, etc.
@router.post('/search/{id_driver}')
def ask_for_voyage(id_driver: str, voyage: SearchVoyageBase):
    """
    Passenger Chose a Driver.
    """
    try:
        driver = drivers.find_driver(db, id_driver)
        price = pricing.price_voyage(voyage, driver)
        client = passenger.find_passenger(db, voyage.passenger.id)
        is_vip = False
        if voyage.is_vip and driver.is_vip and client.is_vip:
            is_vip = True
            price = pricing.add_vip_price(price)
        elif voyage.is_vip:
            raise HTTPException(detail={
                                'message': 'Not Allowed For VIP voyage'},
                                status_code=400)

        confirmed_voyage = VoyageBase(passenger_id=voyage.passenger.id,
                                      driver_id=id_driver, init=voyage.init,
                                      end=voyage.end,
                                      status=VoyageStatus.WAITING.value,
                                      price=price,
                                      start_time=datetime.utcnow(),
                                      end_time=datetime.utcnow(),
                                      is_vip=is_vip)

        id = voyages.create_voyage(db, confirmed_voyage)
        drivers.set_waiting_status(db, id_driver)
        passenger.set_waiting_confirmation_status(db, voyage.passenger.id)

        # send push notif to driver

        return {"final_price": price, "voyage_id": str(id), "message":
                "Waiting for Drivers answer."}

    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error choosing the driver. '
            + str(err)},
            status_code=400)


@router.delete('/search')
def cancel_search(passenger_id: str):
    """
    Passenger Cancels Voyage Search
    """
    passenger.change_status(db, passenger_id, PassengerStatus.CHOOSING.value)