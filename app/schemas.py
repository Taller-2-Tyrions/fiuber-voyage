from pydantic import BaseModel


class Point(BaseModel):
    latitude: float
    longitude: float


class PriceRequest(BaseModel):
    origin: Point
    destination: Point
    distance: float
    is_vip: bool


class PriceResponse(BaseModel):
    price: float


class UserBase(BaseModel):
    day_voyages: int
    month_voyages: int
    seniority: int


class ClientBase(UserBase):
    money: int
    payment_method: str


class ConfirmationPriceRequest(PriceRequest):
    driver: UserBase
