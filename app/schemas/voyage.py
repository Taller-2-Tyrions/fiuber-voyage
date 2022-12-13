from datetime import datetime
from pydantic import BaseModel
from .common import Point
from enum import Enum
from typing import Optional, List


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
    ARRIVING = "ARRIVING"  # Llegando a Origen
    TRAVELLING = "TRAVELLING"  # Ya con Cliente
    FINISHED = "FINISHED"  # Viaje Confirmado Ambos
    CANCELLED = "CANCELLED"  # Viaje Cancelado
    STOPPED = "STOPPED"  # Viaje Cancelado Antes De Confrimado x Chofer


class ComplaintType(Enum):
    STEAL = "STEAL"
    SEXUAL_ASSAULT = "SEXUAL"
    UNSAFE_DRIVING = "UNSAFE DRIVING"
    UNSAFE_CAR = "UNSAFE CAR"
    UNDER_INFLUENCE = "UNDER INFLUENCE"
    AGGRESIVE = "AGGRESIVE"


class UserBase(BaseModel):
    id: str
    location: Point
    is_vip: bool


class DriverBase(UserBase):
    status: DriverStatus


class PassengerBase(UserBase):
    status: PassengerStatus


class SearchVoyageBase(BaseModel):
    passenger_id: str
    init: Point
    end: Point
    is_vip: bool


class ReviewBase(BaseModel):
    score: int
    by_driver: bool
    comment: Optional[str]


class ComplaintBase(BaseModel):
    complaint_type: ComplaintType
    description: str


class VoyageBase(BaseModel):
    passenger_id: str
    driver_id: str
    driver_init_location: Point
    init: Point
    end: Point
    status: VoyageStatus
    price: float
    is_vip: bool
    start_time: datetime
    end_time: datetime
    reviews: List[ReviewBase] = []
    complaints: List[ComplaintBase] = []
