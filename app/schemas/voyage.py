from datetime import datetime
from pydantic import BaseModel
from .common import Point
from enum import Enum


class DriverStatus(Enum):
    SEARCHING = "SEARCHING"  # esta totalmente libre
    WAITING = "WAITING"  # Viaje Confirmado Cliente
    GOING = "GOING"  # Viaje Confirmado Ambos
    TRAVELLING = "TRAVELLING"  # Ya con Cliente
    OFFLINE = "OFFLINE"  # No espero viajes


class PassengerStatus(Enum):
    CHOOSING = "CHOOSING"  # Decidiendo Choferes / estado pasivo.
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"  # Viaje Confirmado Cliente
    WAITING_DRIVER = "WAITING_DRIVER"  # Viaje Confirmado Ambos
    TRAVELLING = "TRAVELLING"  # Ya con Cliente


class VoyageStatus(Enum):
    WAITING = "WAITING"  # Viaje Confirmado Cliente
    STARTING = "STARTING"  # Chofer Yendo A Cliente
    TRAVELLING = "TRAVELLING"  # Ya con Cliente
    FINISHED = "FINISHED"  # Viaje Confirmado Ambos


class UserBase(BaseModel):
    id: str
    location: Point
    is_vip: bool


class DriverBase(UserBase):
    status: DriverStatus


class PassengerBase(UserBase):
    status: PassengerStatus


class SearchVoyageBase(BaseModel):
    passenger: PassengerBase
    init: Point
    end: Point
    is_vip: bool


class VoyageBase(BaseModel):
    passenger_id: str
    driver_id: str
    init: Point
    end: Point
    status: VoyageStatus
    price: float
    is_vip: bool
    start_time: datetime
    end_time: datetime
