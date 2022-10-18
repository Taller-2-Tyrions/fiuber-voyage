from app.crud import voyages
from ..schemas.pricing import PriceRequest
from ..schemas.voyage import DriverBase, SearchVoyageBase
from ..schemas.common import Point
from datetime import datetime, time
from ..crud import drivers

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

"""
# price_voyage = PRICE_PER_METER * distancia + PRICE_PER_MINUTE * duracion
#   seniority del driver indica antiguedad. Al tener mas antiguedad el Driver
#        tendria mas beneficio en el precio de su viaje
#   misma idea con viajes por dia/mes
# price_driver = seniority * DISCOUNT_SENIORITY_DRIVER +  voyage_in_date *
#       DISCOUNT_DAILY_DRIVER + voyage_in_mounth * DISCOUNT_MONTHLY_DRIVER
#   seniority del client simil al Driver
#   misma idea con viajes por dia/mes
# price_client = seniority * DISCOUNT_SENIORITY_CLIENT + voyage_in_date *
#       DISCOUNT_DAILY_CLIENT + voyage_in_mounth * DISCOUNT_MONTHLY_DRIVER
# price_time_await = time_confirmacion * PRICE_WAIT_CONF +
#   time_driver_to_origin * PRICE_ARRIVAL

# total_price = (price_voyage + price_driver + price_client + price_time_await)
#       * PRICE_PER_VIP * NIGHT_PLUS

# Características del conductor (viajes en el día, viajes en el mes,
#       antigüedad) -> AVERAGE_DRIVER_PRICE
# Características del pasajero (viajes en el día, viajes en el mes, antigüedad
#       , saldo)
# Método de pago

# Características del viaje
# (duración --> Google Maps, distancia, posición geográfica, fecha y hora)
# Cantidad de viajes que se realizaron en la última ventana temporal
# (Hora, 30 mins, 10 mins) -> Nosotros
# Día y horario de la realización del viaje
# Tiempo de espera del pasajero para:
# Tiempo hasta que un conductor le confirme
# el viaje --> Variable Actualizable
# Tiempo hasta que el conductor llegue a buscarlo --> Google Maps

# To Do Tener En Cuenta Motor De Reglas ?

"""


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


def estimate_price(id_user: str, voyage: PriceRequest):
    price_voyage = get_price_voyage(voyage)
    price_driver = AVERAGE_DRIVER_PRICE
    price_client = get_price_client(id_user)
    price_time_await = AVERAGE_TIME_AWAIT

    print(price_voyage)
    print(AVERAGE_DRIVER_PRICE)
    print(price_client)
    print(AVERAGE_TIME_AWAIT)

    total_price = price_voyage + price_driver + price_client + price_time_await

    if voyage.is_vip:
        total_price *= PRICE_PER_VIP

    if is_night():
        total_price *= NIGHT_PLUS

    return total_price


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
        prices.update({"location": drivers.get_location(db, id)})

    return prices
