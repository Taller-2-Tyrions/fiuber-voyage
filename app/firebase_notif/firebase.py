from firebase_admin import db as firebase_db

from exponent_server_sdk import (
    PushClient,
    PushMessage
)


def notify(user_id, message, data=None):
    ref = firebase_db.reference("/"+user_id)
    device_token = ref.get()
    mes = PushMessage(to=device_token["token"], body=message, data=data)
    try:
        PushClient().publish(mes)
    except Exception as err:
        print(str(err))


def passenger_choosing(driver_id, voyage):
    notify(driver_id, "Te solicitan un viaje.", voyage)


def notify_driver_accepted(passenger_id, voyage):
    notify(passenger_id, "El conductor esta en camino.", voyage)


def notify_driver_declined(passenger_id, voyage):
    notify(passenger_id, "El conductor rechazo tu viaje.", voyage)


def notify_has_started(passenger_id):
    notify(passenger_id, "Tu viaje ha comenzado.")


def notify_has_finished(passenger_id):
    notify(passenger_id, "Tu viaje ha finalizado.")


def passenger_cancelled(driver_id):
    notify(driver_id, "El pasajero ha cancelado tu viaje.")


def driver_cancelled(passenger_id):
    notify(passenger_id, "El conductor ha cancelado tu viaje.")
