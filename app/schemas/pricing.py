from pydantic import BaseModel
from .common import Point
from typing import List


class PriceUserBase(BaseModel):
    seniority: int
    day_voyages: int
    month_voyages: int


class PriceVoyageBase(BaseModel):
    init: Point
    end: Point
    is_vip: bool


class PriceDriverBase(PriceUserBase):
    id: str
    location: Point
    is_vip: bool


class PriceRequestBase(BaseModel):
    voyage: PriceVoyageBase
    passenger: PriceUserBase
    driver: PriceDriverBase


class PriceRequestsBase(BaseModel):
    voyage: PriceVoyageBase
    passenger: PriceUserBase
    drivers: List[PriceDriverBase]
