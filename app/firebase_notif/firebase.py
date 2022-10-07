from fastapi import APIRouter
from pyfcm import FCMNotification
import requests
import json

router = APIRouter(
    prefix="/prueba-firebase",
    tags=['PRUEBA FIREBASE']
)


@router.get('/')
def send_push_notif():
    serverToken = 'AAAAWmYVtJQ:APA91bExlX_ItIPkBoltvvq5BYozkaDZ5JUnlMjJJRy-gu9EM_GmQq0N7uKsJGCPEBsBbiNVwXV5LkqqcqFIdSI62xiX6pVt2ZW7oPZRu638ixYYq1ScWAMpFrtZDxjDTC2KVM0tMdDQ'
    deviceToken = 'UTouL4K78IXX3bpzKtP6ta'

    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

    body = {
            'notification': {'title': 'Sending push form python script',
                                'body': 'New Message'
                                },
            'to':
                deviceToken,
            'priority': 'high',
            #   'data': dataPayLoad,
            }
    response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
    print(response.status_code)

    print(response.json())



    # try:
    #     push_service = FCMNotification(
    #                     api_key="AAAAWmYVtJQ:APA91bExlX_ItIPkBoltvvq5BYozkaDZ5JUnlMjJJRy-gu9EM_GmQq0N7uKsJGCPEBsBbiNVwXV5LkqqcqFIdSI62xiX6pVt2ZW7oPZRu638ixYYq1ScWAMpFrtZDxjDTC2KVM0tMdDQ")
    #     print("error1")
    #     registration_id = "UTouL4K78IXX3bpzKtP6ta"
    #     message_title = "Uber update"
    #     message_body = "Hi john, your customized news for today is ready"
    #     result = push_service.notify_single_device(
    #                         registration_id=registration_id,
    #                         message_title=message_title,
    #                         message_body=message_body)
    #     print(result)
    # except Exception as err: 
    #     return {"error": str(err)}

# # This registration token comes from the client FCM SDKs.
# #registration_token = 'YOUR_REGISTRATION_TOKEN'

# def notify_drivers(near_drivers, voyage: InitVoyageBase):
#     #To do
#     print("Aca se envia notificacion")
#     return 0

