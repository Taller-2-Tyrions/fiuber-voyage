from pydantic import BaseModel
from .common import Point


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
    is_searching: bool
