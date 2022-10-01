from fastapi import APIRouter
from ..schemas import PriceRequest, PriceResponse


router = APIRouter(
    prefix="/price",
    tags=['Price']
)


@router.post('/{id_user}')
async def price(id_user: str, voyage: PriceRequest):
    # To Do Check Modality Access (Nosotros O Gateway?)
    # To Do Tener En Cuenta Motor De Reglas

    return PriceResponse(price=2)
