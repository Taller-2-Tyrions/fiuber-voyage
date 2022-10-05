from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from datetime import datetime


def create_searcher(db, voyage):
    try:
        user_encoded = jsonable_encoder(voyage)
        user_encoded.update({"time": datetime.now()})
        db["clients"].insert_one(user_encoded)
    except Exception as err:
        raise HTTPException(detail={
            'message': 'There was an error accessing the clients database '
            + str(err)},
            status_code=400)
