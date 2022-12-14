from pydantic import BaseModel


class Point(BaseModel):
    longitude: float
    latitude: float
