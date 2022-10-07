from fastapi import APIRouter
from ..schemas.voyage import InitVoyageBase
from pyfcm import FCMNotification


router = APIRouter(
    prefix="/prueba-firebase",
    tags=['PRUEBA FIREBASE']
)


@router.post('/')
def send_push_notif(voyage_info, id_driver):
    push_service = FCMNotification(
                    api_key="AIzaSyBSenFicB4rNCqRO183gmoMILDImbTR84Y")

    registration_id = "UTouL4K78IXX3bpzKtP6ta"
    message_title = "Uber update"
    message_body = "Hi john, your customized news for today is ready"
    result = push_service.notify_single_device(
                           registration_id=registration_id,
                           message_title=message_title,
                           message_body=message_body)
    print(result)


# This registration token comes from the client FCM SDKs.
#registration_token = 'YOUR_REGISTRATION_TOKEN'

def notify_drivers(near_drivers, voyage: InitVoyageBase):
    #To do
    print("Aca se envia notificacion")
    return 0

