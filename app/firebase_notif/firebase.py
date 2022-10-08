from fastapi import APIRouter
from pyfcm import FCMNotification
import requests
import json

from oauth2client.service_account import ServiceAccountCredentials

from firebase_admin import messaging
import firebase_admin

# [START get_service_account_tokens]
from firebase_admin import credentials

cred = credentials.Certificate('firebasekey2.json')
access_token_info = cred.get_access_token()

access_token = access_token_info.access_token
expiration_time = access_token_info.expiry
# Attach access_token to HTTPS request in the "Authorization: Bearer" header
# After expiration_time, you must generate a new access token
# [END get_service_account_tokens]

print('The access token {} expires at {}'.format(access_token, expiration_time))
firebase_admin.initialize_app(cred)

router = APIRouter(
    prefix="/prueba-firebase",
    tags=['PRUEBA FIREBASE']
)

#server_apikey = 'AAAAWmYVtJQ:APA91bFbBzcX2AM7w4p_Nt5QiCCDhRiTSG46SbQcn83_DaMj-pnZzktbd_7r9MmkRfuLNve1S0yLHPT-_mDoEb756-QTgE8bapcGlWKtSAOVEQgY27t03Y2xa3ngBeEGJgvK9s7087zb'
server_apikey = 'AAAAODISeRA:APA91bEYVUP4uUdemxUCP_5xT0d9OwC1auxZA1QNkjdyh_pAtAMrZ6pf5HDXZsQe3BCGk-wwKJp4GGgzH4WUhjSF7XwIXo-kyixviKYbQfjbAS_Hx__9qxHtHHP_wjDq-WOKNGwMMOe6'
registration_id = 'f8UDdNguSsaxwhwq5UTtug:APA91bGSeCb_LFUxVtYU_G24H_5Ka3dW65T9sSGkQ8OI9pISZJ6ZasNnS86wh9XOPM1XbFzQaXHk3XIZzT60fSFr9YZY2zC6YUul338Mh-0Ww2r0pMwE2HpkR91z-zFhh2SYZBxcLed0'

api_key = 'AIzaSyBD7RU6CV4LP2uy_Fktm19Jcy6EdUCkbHs'

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

#projectId = 'fiuber-36b86'#'test-fcm-f9779'
projectId = 'fiuber-363101'
def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      'firebasekey2.json', SCOPES)
  access_token_info = credentials.get_access_token()
  return access_token_info.access_token


@router.get('/noti-old')
def send_push_notif():
    #deviceToken = 'UTouL4K78IXX3bpzKtP6ta'

    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + server_apikey,
    }

    body = {
            'notification': {'title': 'Sending push form python script',
                                'body': 'New Message'
                                },
            'to': registration_id,
            'priority': 'high'
            }
    response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
    print(response.status_code)

    print(response.json())


@router.get('/noti-fcmNotification')
def send_push_notif2():
    try:
        push_service = FCMNotification(
                        api_key=server_apikey)
        print("error1")
        registration_id = registration_id
        message_title = "Uber update"
        message_body = "Hi john, your customized news for today is ready"
        result = push_service.notify_single_device(
                            registration_id=registration_id,
                            message_title=message_title,
                            message_body=message_body)
        print(result)
    except Exception as err: 
        return {"error": str(err)}

@router.get('/noti-new')
def send_push_notif3():

    registration_id = 'f8UDdNguSsaxwhwq5UTtug:APA91bGSeCb_LFUxVtYU_G24H_5Ka3dW65T9sSGkQ8OI9pISZJ6ZasNnS86wh9XOPM1XbFzQaXHk3XIZzT60fSFr9YZY2zC6YUul338Mh-0Ww2r0pMwE2HpkR91z-zFhh2SYZBxcLed0'
    access_token = _get_access_token()
    headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json; UTF-8',
    }

    # body = {
    #         'notification': {'title': 'Sending push form python script',
    #                             'body': 'New Message'
    #                             },
    #         'to':
    #             registration_id,
    #         'priority': 'high',
    #         #   'data': dataPayLoad,
    #         }
    
    # Funciono!
    # body = {
    #   "message": {
    #     "topic": "news",
    #     "notification": {
    #       "title": "Breaking News",
    #       "body": "New news story available."
    #     },
    #     "data": {
    #       "story_id": "story_12345"
    #     }
    #   }
    # }
    
    #No funciono
    # body = {
    #    "message":{
    #       "token":registration_id,
    #       "notification":{
    #         "body":"This is an FCM notification message!",
    #         "title":"FCM Message"
    #       }
    #    }
    # }

    #"token": registration_id+":"+access_token,

    body = {
       "message":{
          "token": registration_id,
          "notification":{
            "body":"This is an FCM notification message!",
            "title":"FCM Message"
          }
       }
    }

    # POST https://fcm.googleapis.com/v1/projects/myproject-b5ae1/messages:send
    response = requests.post("https://fcm.googleapis.com/v1/projects/"+projectId+"/messages:send",headers = headers, data=json.dumps(body))
    print(response.status_code)

    print("response: "+str(response.json()))

@router.get('/subscribe_to_topic')
def subscribe_to_topic():
    topic = "topic"
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        registration_id
    ]

    # Subscribe the devices corresponding to the registration tokens to the
    # topic.
    response = messaging.subscribe_to_topic(registration_tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were subscribed successfully')

@router.get('/send_to_token')
def send_to_token():
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.

    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token=registration_id,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_token]

@router.get('/send_simple_notification')
def send_simple_notification():
    # [START send_to_topic]
    # The topic name can be optionally prefixed with "/topics/".
    topic = 'topic'

    # See documentation on defining a message payload.
    message = messaging.Message(
        data= {"data":"Holaaaaaaaa"},
        token= registration_id
    )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_topic]
