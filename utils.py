import boto3
import json
from botocore.vendored import requests

from messages import url_error, url_credentials_error


def validate_if_logged_in(event):
    if "sessionAttributes" in event and event["sessionAttributes"] != None:
        if "url" in event['sessionAttributes'] and event['sessionAttributes']["url"] and \
            "username" in event['sessionAttributes'] and event['sessionAttributes']["username"] and \
            "password" in event['sessionAttributes'] and event['sessionAttributes']["password"]:
            return True
        else:
            return False
    else:
        return False



def generate_response_code(event, slots=None, **kwargs):
    print(kwargs)

    dialog_type = kwargs["dialog_type"]

    # intialize empty dict struture
    return_response = dict()
    return_response["dialogAction"] = dict()

    if "sessionattributes" in kwargs:
        return_response["sessionAttributes"] = kwargs["sessionattributes"]

    # TO fill the dict with Slots and SKIP if we do not want slots to be part of return
    # response

    if slots == "SKIP":
        pass
    elif slots:
        return_response["dialogAction"]["slots"] = slots
    else:
        return_response["dialogAction"]["slots"] = {}

    # here we do create all out complex reponse stucture

    if dialog_type == "ELICITSLOT":
        return_response["dialogAction"]["type"] = "ElicitSlot"
        return_response["dialogAction"]["intentName"] = kwargs["intent"]
        return_response["dialogAction"]["slotToElicit"] = kwargs["slot_to_elicit"]
        return_response["dialogAction"]["message"] = { "contentType": "PlainText",
                                                       "content": kwargs["message"]}
    elif dialog_type == "ELICIT":
        return_response["dialogAction"]["type"] = "ElicitIntent"
        return_response["dialogAction"]["message"] = { "contentType": "PlainText",
                                                       "content": kwargs["message"]}

    elif dialog_type == "DELEGATE":
        return_response["dialogAction"]["type"] = "Delegate"

    elif dialog_type == "CONFIRM":
        return_response["dialogAction"]["type"] = "ConfirmIntent"
        return_response["dialogAction"]["intentName"] = kwargs["fulfill_state"]
        return_response["dialogAction"]["message"] = { "contentType": "PlainText",
                                                       "content": kwargs["message"]}
    elif dialog_type == "CLOSEFULLFILLED":
        return_response["dialogAction"]["type"] = "Close"
        return_response["dialogAction"]["fulfillmentState"] = "Fulfilled"
        return_response["dialogAction"]["message"] = { "contentType": "PlainText",
                                                       "content": kwargs["message"]}

    elif dialog_type == "CLOSEFAILED":
        return_response["dialogAction"]["type"] = "Close"
        return_response["dialogAction"]["fulfillmentState"] = "Failed"
        return_response["dialogAction"]["message"] = { "contentType": "PlainText",
                                                       "content": kwargs["message"]}

    elif dialog_type == "DELEGATE":
        return_response["dialogAction"]["type"] = "Delegate"


    return return_response


def generate_url(base_url,type_of_request,**kwargs):

    if type_of_request == "EPG_URL":
        return "{}node/mo/uni/tn-{}/ap-{}/epg-{}.json".format(kwargs["base_url"])

    elif type_of_request == "LOGIN":

        pass


def make_post_api_call(url, payload=None, cookies=None):

    # Try catch is to catch exception if the URL is not reachable randiom.com
    try:
        if cookies:
            web_request_data = requests.post(url, data=payload, cookies=cookies, verify=False)
        else:
            web_request_data = requests.post(url, data=payload, verify=False)
        return web_request_data
    except Exception:
        return None


def make_get_api_call(url, cookies=None):

    try:
        if cookies:
            web_request_data = requests.get(url, cookies=cookies, verify=False)
        else:
            web_request_data = requests.get(url, verify=False)
        return web_request_data
    except Exception:
        return None



def get_logindata_from_ddb():

    # Removed AK / SK as we are using role with Lambda. SO AWS will automatically provide STS credentials to boto3

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('apic-details')
    response = table.get_item(Key={'apic-url':'API_DC_URL_SANDBOX'})



    return response


def aci_login(base_url, username, password):

    name_pwd = {'aaaUser': {'attributes': {'name': username, 'pwd': password}}}
    json_credentials = json.dumps(name_pwd)

    login_url = "{}{}".format(base_url,'aaaLogin.json')
    web_response = make_post_api_call(login_url, payload=json_credentials)

    if web_response.status_code == 404:
        # cookies = 'Please Check the URI as we have a 404 Error'
        return url_error

    elif web_response.status_code == 401:
        # cookies= 'Please Check the credentials as we have a 401 Error'
        return url_credentials_error

    else:
        auth = json.loads(web_response.text)
        login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
        auth_token = login_attributes['token']
        cookies = dict()
        cookies['APIC-Cookie'] = auth_token

        return cookies
