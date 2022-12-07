import requests
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from ..schemas.voyage import PassengerStatus, ReviewBase
from ..schemas.voyage import DriverStatus, VoyageStatus
from ..schemas.pricing import PriceDriverBase, PriceUserBase, PriceVoyageBase
from ..schemas.pricing import PriceRequestBase
from ..database.mongo import db
from ..crud import drivers, passenger, voyages
from ..firebase_notif import firebase as notifications
from dotenv import load_dotenv
import os

load_dotenv()

PRICING_URL = os.getenv("PRICING_URL")

router = APIRouter(
    prefix="/voyage",
    tags=['Voyage']
)


def get_price_request(voyage):
    id_p = voyage.get("passenger_id")
    is_vip = voyage.get("is_vip")
    id_driver = voyage.get("driver_id")
    driver = drivers.find_driver(db, id_driver)
    seniority_p, daily_p, monthly_p = voyages.get_history(db,
                                                          id_p, False)

    price_passenger = PriceUserBase(seniority=seniority_p,
                                    day_voyages=daily_p,
                                    month_voyages=monthly_p)
    price_voyage = PriceVoyageBase(init=voyage.get("driver_init_location"),
                                   end=driver.get("location"),
                                   is_vip=is_vip)
    seniority_d, daily_d, monthly_d = voyages.get_history(db,
                                                          id_driver, True)
    start_loc = voyage.get("driver_init_location")
    price_driver = PriceDriverBase(seniority=seniority_d,
                                   day_voyages=daily_d,
                                   month_voyages=monthly_d,
                                   id=id_driver,
                                   is_vip=is_vip,
                                   location=start_loc)

    price_request = PriceRequestBase(voyage=price_voyage,
                                     passenger=price_passenger,
                                     driver=price_driver)

    return price_request


def price_cancellation(voyage):
    id_p = voyage.get("passenger_id")
    id_driver = voyage.get("driver_id")
    price_request = get_price_request(voyage)

    req = requests.post(PRICING_URL+"pricing/voyage",
                        json=jsonable_encoder(price_request))

    if (req.status_code != status.HTTP_200_OK):
        raise HTTPException(detail={'message': 'Error Cotizando'},
                            status_code=400)

    return {"senderId": id_p, "receiverId": id_driver,
            "amountInEthers": req.json()}


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

    is_starting = voyage_status == VoyageStatus.STARTING.value
    is_travelling = voyage_status == VoyageStatus.TRAVELLING.value
    is_travelling_passenger = is_travelling and is_passenger

    if voyage_status == VoyageStatus.WAITING.value and is_passenger:
        print("Is Waiting")
        drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
        passenger.change_status(db, passenger_id,
                                PassengerStatus.CHOOSING.value)
    elif is_starting or is_travelling_passenger:
        print("Is Starting/Travelling")
        drivers.change_status(db, driver_id, DriverStatus.SEARCHING.value)
        passenger.change_status(db, passenger_id,
                                PassengerStatus.CHOOSING.value)
        if is_passenger:
            print("Cancel Multa")
            notifications.passenger_cancelled(driver_id)
            voyages.change_status(db, voyage_id, VoyageStatus.CANCELLED.value)
            return price_cancellation(voyage)
        else:
            notifications.driver_cancelled(passenger_id)
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


@router.get('/calification/{user_id}/{is_driver}')
def get_calification(user_id: str, is_driver: bool):
    """
    Get User Global calification
    """
    try:
        return {"calification":
                voyages.get_average_score(db, user_id, is_driver)}
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the database '
            + str(err)},
            status_code=400)


@router.get('/count/{user_id}/{is_driver}')
def get_count(user_id: str, is_driver: bool):
    """
    Get User Cuantity of Voyages
    """
    try:
        return {"count":
                voyages.get_number_voyages(db, user_id, is_driver)}
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the database '
            + str(err)},
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


@router.get('/review/{user_id}/{is_driver}')
def get_last_reviews(user_id: str, is_driver: bool, number: int = 5):
    """
    Get User Last Reviews
    """
    try:
        return {"reviews":
                voyages.get_reviews(db, user_id, is_driver, number)}
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the database '
            + str(err)},
            status_code=400)


@router.get('/status/{user_id}')
def get_status(user_id: str):
    """
    Return the last state the user was in
    """
    driver = drivers.find_driver(db, user_id)
    client = passenger.find_passenger(db, user_id)

    if not client and not driver:
        raise HTTPException(detail={'message': 'User Not Loaded'},
                            status_code=400)

    if driver and client:
        client_status = client.get("status")
        driver_status = driver.get("status")

        is_driver = driver_status != DriverStatus.OFFLINE.value
        is_passenger = client_status != PassengerStatus.CHOOSING.value

        if is_driver and is_passenger:
            raise HTTPException(detail={'message': 'User Badly Closed'},
                                status_code=400)
    else:
        is_driver = client is None

    if not is_driver:
        status = client.get("status")
        is_choosing = status == PassengerStatus.CHOOSING.value

        if not is_choosing:
            id_voyage = voyages.get_current_voyage(db, user_id,
                                                   is_driver=False)
            return {"Rol": "Passenger", "Status": status, "Voyage": id_voyage}
        else:
            return {"Rol": "Passenger", "Status": status}
    else:
        status = driver.get("status")
        is_searching = status == DriverStatus.SEARCHING.value
        is_offline = status == DriverStatus.OFFLINE.value

        if not is_searching and not is_offline:
            id_voyage = voyages.get_current_voyage(db, user_id,
                                                   is_driver=True)
            return {"Rol": "Driver", "Status": status, "Voyage": id_voyage}
        else:
            return {"Rol": "Driver", "Status": status}


@router.get('/info/{voyage_id}/{user_caller}')
def get_voyage_info(voyage_id: str, user_caller: str):
    """
    Return The info of voyage asked
    """
    try:
        data = voyages.find_voyage(db, voyage_id)
        if not data:
            raise Exception("No Voyage Found")
        is_passenger = data.get("passenger_id") != user_caller
        is_driver = data.get("driver_id") != user_caller
        if not is_driver and not is_passenger:
            raise Exception("Not Allowed")
        return data
    except Exception as err:
        raise HTTPException(detail={'message': f"Can't Access Database {err}"},
                            status_code=400)


@router.get('/location/{voyage_id}/{user_caller}')
def get_driver_info(voyage_id: str, user_caller: str):
    """
    Return The location of driver
    """
    try:
        data = get_voyage_info(voyage_id, user_caller)

        driver = data.get("driver_id")

        return drivers.get_location(db, driver)
    except Exception:
        raise HTTPException(detail={'message': "Can't Access Database"},
                            status_code=400)


@router.get('/complaints')
def get_complaints():
    """
    Return all complaints
    """
    try:
        return voyages.get_all_complaints(db)
    except Exception:
        raise HTTPException(detail={'message': "Can't Access Database"},
                            status_code=400)
