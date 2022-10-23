from datetime import datetime
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from app.schemas.common import Point
from fastapi.encoders import jsonable_encoder
from ..schemas.voyage import ComplaintBase, DriverStatus, PassengerBase
from ..schemas.voyage import SearchVoyageBase, PassengerStatus
from ..schemas.voyage import VoyageBase, VoyageStatus
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..prices import pricing
from ..firebase_notif import firebase as notifications

router = APIRouter(
    prefix="/voyage/passenger",
    tags=['Voyage Passenger']
)


@router.post('/signup/{id_passenger}')
def add_passenger(id_passenger: str):
    """
    Add Passenger To List
    """
    try:
        location = Point(longitude=0.0, latitude=0.0)
        person = PassengerBase(id=id_passenger, location=location,
                               status=PassengerStatus.CHOOSING.value,
                               is_vip=False)
        passenger.create_passenger(db, person)
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
        return passenger.update_passenger(db, passenger_id, changes)
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

        for driver, price in prices.items():
            final_prices.update({driver: {"Standard": price}})

        for driver, price in vip_prices.items():
            before = final_prices.get(driver, {})
            before.update({"VIP": price})
            final_prices.update({driver: before})

        return final_prices
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error searching drivers '
            + str(err)},
            status_code=400)


@router.post('/search/{id_driver}')
def ask_for_voyage(id_driver: str, voyage: SearchVoyageBase):
    """
    Passenger Chose a Driver.
    """
    driver = drivers.find_driver(db, id_driver)
    if not driver:
        raise HTTPException(detail={
                            'message': 'Driver Not Found'},
                            status_code=400)
    client = passenger.find_passenger(db, voyage.passenger_id)
    if not client:
        raise HTTPException(detail={
                            'message': 'Passenger Not Found'},
                            status_code=400)
    try:
        price = pricing.price_voyage(voyage, driver)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error getting the price. '
            + str(err)},
            status_code=400)

    is_vip = False
    if voyage.is_vip and driver.get("is_vip") and client.get("is_vip"):
        is_vip = True
        price = pricing.add_vip_price(price)
    elif voyage.is_vip:
        raise HTTPException(detail={
                            'message': 'Not Allowed For VIP voyage'},
                            status_code=400)

    confirmed_voyage = VoyageBase(passenger_id=voyage.passenger_id,
                                  driver_id=id_driver, init=voyage.init,
                                  end=voyage.end,
                                  status=VoyageStatus.WAITING.value,
                                  price=price,
                                  start_time=datetime.utcnow(),
                                  end_time=datetime.utcnow(),
                                  is_vip=is_vip)
    if driver.get("status") != DriverStatus.SEARCHING.value:
        raise HTTPException(detail={
                            'message': 'Driver not available'},
                            status_code=400)
    if client.get("status") != PassengerStatus.CHOOSING.value:
        raise HTTPException(detail={
                            'message': 'Passenger not available'},
                            status_code=400)

    id = voyages.create_voyage(db, confirmed_voyage)
    drivers.set_waiting_status(db, id_driver)
    passenger.set_waiting_confirmation_status(db, voyage.passenger_id)

    notifications.passenger_choosing(id_driver,
                                     jsonable_encoder(confirmed_voyage))

    return {"final_price": price, "voyage_id": id, "message":
            "Waiting for Drivers answer."}


@router.delete('/search/{passenger_id}')
def cancel_search(passenger_id: str):
    """
    Passenger Cancels Voyage Search
    """
    passenger.change_status(db, passenger_id, PassengerStatus.CHOOSING.value)


@router.post('/complaint/{voyage_id}/{caller_id}')
def add_complaint(voyage_id: str,  caller_id: str, complaint: ComplaintBase):
    """
    Passenger Load A Complaint Of Voyage
    """
    voyage = voyages.find_voyage(db, voyage_id)
    if not voyage:
        raise HTTPException(detail={'message': 'Non Existent Voyage'},
                            status_code=400)

    saved_id = voyage.get("passenger_id")
    if caller_id != saved_id:
        raise HTTPException(detail={'message': 'Passenger Not In Voyage'},
                            status_code=400)

    voyages.add_complaint(db, voyage_id, complaint)
    # Notify Admins

@router.get('/test/{_origin_point}/{_dest_point}')
def testDistance(_origin_point: str, _dest_point: str):
    print(_origin_point)
    print(_dest_point)
    op = _origin_point.split(",")[0]
    op2 = _origin_point.split(",")[1]
    dp = _dest_point.split(",")[0]
    dp2 = _dest_point.split(",")[1]
    origin_point = Point(longitude= float(op2), latitude= float(op))
    dest_point = Point(longitude=float(dp2), latitude= float(dp))
    
    d = pricing.distance_to(origin_point, dest_point)
    print("distance: "+str(d))
    return d