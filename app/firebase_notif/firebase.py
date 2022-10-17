from firebase_admin import db as firebase_db
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)



def notify(user_id, message):
    ref = firebase_db.reference("/"+user_id)
    device_token = ref.get()
    mes = PushMessage(to=device_token["token"], body=message)
    PushClient().publish(mes)
