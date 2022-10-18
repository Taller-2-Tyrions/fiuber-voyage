from datetime import datetime, time

from app.crud import voyages
from ..schemas.pricing import PriceRequest
from ..schemas.voyage import DriverBase, SearchVoyageBase
from ..schemas.common import Point
from ..database.mongo import db


PRICE_PER_METER = 1.5
PRICE_PER_MINUTE = 1.5
PRICE_PER_VIP = 1.2
NIGHT_PLUS = 1.2
DISCOUNT_SENIORITY_DRIVER = 1
DISCOUNT_DAILY_DRIVER = 1
DISCOUNT_MONTHLY_DRIVER = 1
DISCOUNT_SENIORITY_CLIENT = 1
DISCOUNT_DAILY_CLIENT = 1
DISCOUNT_MONTHLY_CLIENT = 1
PRICE_WAIT_CONF = 1
PRICE_ARRIVAL = 1

BASE_PRICE_CLIENT = 50
MAX_DISCOUNT_DRIVER = 50

NIGHT_START = time(20, 0)
NIGHT_END = time(6, 0)

AVERAGE_DRIVER_PRICE = 10
AVERAGE_TIME_AWAIT = 10


def distance_to(point_a, point_b):
    latitude_dist = abs(point_a.latitude - point_b.latitude)
    longitude_dist = abs(point_a.longitude - point_b.longitude)

    return latitude_dist + longitude_dist


def time_to(point_a, point_b):
    return distance_to(point_a, point_b)*0.1


def get_price_driver(id_driver):
    today_voyages = voyages.get_date_voyages(db, id_driver,
                                             is_driver=True, is_daily=True)
    month_voyages = voyages.get_date_voyages(db, id_driver,
                                             is_driver=True, is_daily=False)
    seniority = voyages.get_seniority(db, id_driver, is_driver=True)

    seniority = 1

    total_price = 0

    total_price += today_voyages * DISCOUNT_DAILY_DRIVER
    total_price += month_voyages * DISCOUNT_MONTHLY_DRIVER
    total_price += seniority * DISCOUNT_SENIORITY_DRIVER

    if total_price > MAX_DISCOUNT_DRIVER:
        total_price = MAX_DISCOUNT_DRIVER

    return total_price


def get_price_client(id_user):
    today_voyages = voyages.get_date_voyages(db, id_user,
                                             is_driver=False, is_daily=True)
    month_voyages = voyages.get_date_voyages(db, id_user,
                                             is_driver=False, is_daily=False)
    seniority = voyages.get_seniority(db, id_user, is_driver=False)

    seniority = 1

    total_price = BASE_PRICE_CLIENT

    total_price -= today_voyages * DISCOUNT_DAILY_CLIENT
    total_price -= month_voyages * DISCOUNT_MONTHLY_CLIENT
    total_price -= seniority * DISCOUNT_SENIORITY_CLIENT

    if total_price < 0:
        total_price = 0

    return total_price


def is_night():
    now = datetime.utcnow()
    now_time = now.time()

    if now_time >= NIGHT_START or now_time <= NIGHT_END:
        return True

    return False


def get_price_voyage(voyage: PriceRequest):
    price = distance_to(voyage.init, voyage.end) * PRICE_PER_METER
    price += time_to(voyage.init, voyage.end) * PRICE_PER_MINUTE

    return price


def get_time_await(driver, init):
    location = driver.get("location")
    location = Point(latitude=location.get("latitude"),
                     longitude=location.get("longitude"))
    price = time_to(location, init)*PRICE_PER_MINUTE
    price += distance_to(location, init)*PRICE_PER_METER

    return price


def price_voyage(voyage: SearchVoyageBase, driver: DriverBase):
    price_voyage = get_price_voyage(voyage)
    price_driver = get_price_driver(driver.get("id"))
    price_client = get_price_client(voyage.passenger_id)
    price_time_await = get_time_await(driver, voyage.init)

    total_price = price_voyage + price_driver + price_client + price_time_await

    if is_night():
        total_price *= NIGHT_PLUS

    return total_price


def add_vip_price(price):
    return price * PRICE_PER_VIP


def get_voyage_info(voyage, near_drivers, is_vip):
    prices = {}

    for driver in near_drivers:
        price = price_voyage(voyage, driver)
        id = driver.get("id")
        if is_vip:
            price = add_vip_price(price)
        prices.update({id: price})

    return prices
