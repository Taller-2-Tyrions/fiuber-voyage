import requests
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.common import Point
from ..schemas.voyage import ComplaintBase, DriverStatus, PassengerBase
from ..schemas.voyage import SearchVoyageBase, PassengerStatus
from ..schemas.voyage import VoyageBase, VoyageStatus
from ..schemas.pricing import PriceDriverBase, PriceUserBase, PriceVoyageBase
from ..schemas.pricing import PriceRequestsBase, PriceRequestBase
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..firebase_notif import firebase as notifications
from dotenv import load_dotenv
import os

load_dotenv()

PRICING_URL = os.getenv("PRICING_URL")


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

        base_url = PRICING_URL+"pricing/voyages"

        if voyage.is_vip:
            vip_drivers = drivers.get_nearest_drivers_vip(db,
                                                          location_searched)

            price_request = get_price_requests(voyage, vip_drivers, True)

            req = requests.post(base_url, json=jsonable_encoder(price_request))
            data = req.json()
            if (req.status_code != status.HTTP_200_OK):
                raise HTTPException(detail=data["detail"],
                                    status_code=req.status_code)
            vip_prices = data

        price_request = get_price_requests(voyage, near_drivers, False)

        req = requests.post(base_url, json=jsonable_encoder(price_request))
        data = req.json()
        if (req.status_code != status.HTTP_200_OK):
            raise HTTPException(detail=data["detail"],
                                status_code=req.status_code)
        prices = data

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
    pass_status = client.get("status")
    if pass_status != PassengerStatus.CHOOSING.value:
        raise HTTPException(detail={
                            'message': "Cant Order Voyage If Not Searching"},
                            status_code=400)
    try:
        if voyage.is_vip and driver.get("is_vip") and client.get("is_vip"):
            is_vip = True
        elif voyage.is_vip:
            raise Exception('Not Allowed For VIP voyage')
        else:
            is_vip = False

        price_request = get_price_request(voyage, driver, is_vip)

        req = requests.post(PRICING_URL+"pricing/voyage",
                            json=jsonable_encoder(price_request))
        data = req.json()
        if (req.status_code != status.HTTP_200_OK):
            raise HTTPException(detail=data["detail"],
                                status_code=req.status_code)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error getting the price. '
            + str(err)},
            status_code=400)

    confirmed_voyage = VoyageBase(passenger_id=voyage.passenger_id,
                                  driver_id=id_driver, init=voyage.init,
                                  driver_init_location=driver.get("location"),
                                  end=voyage.end,
                                  status=VoyageStatus.WAITING.value,
                                  price=data,
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

    return {"final_price": data, "voyage_id": id, "message":
            "Waiting for Drivers answer."}


@router.post("/confirm/{voyage_id}/{passenger_id}/{status}")
def confirm_voyage(voyage_id: str, passenger_id: str, status: bool):
    """
    Inform If Passenger Is Capable Of Paying Voyage
    """
    if not status:
        voyages.delete_voyage(db, voyage_id)
    else:
        voyage = voyages.find_voyage(db, voyage_id)
        if not voyage:
            raise HTTPException(detail={
                                'message': 'There is no Voyage To Confirm'},
                                status_code=400)

        id_passenger = voyage.get("passenger_id")
        if passenger_id != id_passenger:
            raise HTTPException(detail={
                                'message': 'Not your Voyage To Confirm'},
                                status_code=400)

        id_driver = voyage.get("driver_id")

        drivers.set_waiting_status(db, id_driver)
        passenger.set_waiting_confirmation_status(db, passenger_id)

        voyage_noti = str({"voyage_id": id,
                          "voyage_confirmation": voyage})

        notifications.passenger_choosing(id_driver, voyage_noti)


@router.delete('/search/{passenger_id}')
def cancel_search(passenger_id: str):
    """
    Passenger Cancels Voyage Search
    """
    try:
        id_voyage = voyages.get_current_voyage(db, passenger_id,
                                               is_driver=False)
        voyages.set_cancelled_status(db, id_voyage)
        passenger.change_status(db, passenger_id,
                                PassengerStatus.CHOOSING.value)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error updating voyage '
            + str(err)},
            status_code=400)


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


def get_price_request(voyage: SearchVoyageBase, driver, is_vip):
    id_p = voyage.passenger_id
    id_driver = driver.get("id")
    seniority_p, daily_p, monthly_p = voyages.get_history(db,
                                                          id_p, False)

    price_passenger = PriceUserBase(seniority=seniority_p,
                                    day_voyages=daily_p,
                                    month_voyages=monthly_p)
    price_voyage = PriceVoyageBase(init=voyage.init,
                                   end=voyage.end,
                                   is_vip=is_vip)
    seniority_d, daily_d, monthly_d = voyages.get_history(db,
                                                          id_driver, True)

    price_driver = PriceDriverBase(seniority=seniority_d,
                                   day_voyages=daily_d,
                                   month_voyages=monthly_d,
                                   id=id_driver,
                                   is_vip=driver.get("is_vip"),
                                   location=driver.get("location"))

    price_request = PriceRequestBase(voyage=price_voyage,
                                     passenger=price_passenger,
                                     driver=price_driver)

    return price_request


def get_price_requests(voyage: SearchVoyageBase, drivers, is_vip):
    id_p = voyage.passenger_id
    seniority_p, daily_p, monthly_p = voyages.get_history(db,
                                                          id_p, False)

    price_passenger = PriceUserBase(seniority=seniority_p,
                                    day_voyages=daily_p,
                                    month_voyages=monthly_p)
    price_voyage = PriceVoyageBase(init=voyage.init,
                                   end=voyage.end,
                                   is_vip=is_vip)

    price_drivers = []

    for driver in drivers:
        id_driver = driver.get("id")
        seniority_d, daily_d, monthly_d = voyages.get_history(db,
                                                              id_driver, True)
        price_driver = PriceDriverBase(seniority=seniority_d,
                                       day_voyages=daily_d,
                                       month_voyages=monthly_d,
                                       id=id_driver,
                                       is_vip=driver.get("is_vip"),
                                       location=driver.get("location"))
        price_drivers.append(price_driver)

    price_request = PriceRequestsBase(voyage=price_voyage,
                                      passenger=price_passenger,
                                      drivers=price_drivers)

    return price_request
