from pydantic import BaseModel


class Point(BaseModel):
    latitude: float
    longitude: float


class PriceRequest(BaseModel):
    origin: Point
    destination: Point
    is_vip: bool


class PriceResponse(BaseModel):
    price: float
