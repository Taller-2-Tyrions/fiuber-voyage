from ..schemas.voyage import InitVoyageBase

# This registration token comes from the client FCM SDKs.
#registration_token = 'YOUR_REGISTRATION_TOKEN'

def notify_drivers(near_drivers, voyage: InitVoyageBase):
    #To do
    print("Aca se envia notificacion")
    return 0

def send_push_notif(voyage_info, id_driver):
    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )
    
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)