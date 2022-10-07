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
    WAITING = "WAITING"  # Viaje Confirmado Cliente
    GOING = "GOING"  # Viaje Confirmado Ambos
    TRAVELLING = "TRAVELLING"  # Ya con Cliente


class PersonBase(BaseModel):
    id: str
    name: str
    last_name: str


class InitVoyageBase(BaseModel):
    passenger: PersonBase
    init: Point
    end: Point


class DriverBase(BaseModel):
    id: str
    location: Point
    status: DriverStatus


class PassengerBase(BaseModel):
    id: str
    location: Point
    status: PassengerStatus
