"""
AWS lambda code by end of part 2 of programming alexa series
"""

from __future__ import print_function
import random
import requests
from aci_login_work import aci_login
import boto3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from string import Template
from messages import tenant_created_message,tenant_failed_message,tenant_exists_message,tenant_ap_exist_message, tenant_exists_ap_created_message,tenant_not_exist_message,snapshot_created_template,snapshot_failed,ap_epg_exist_message,ap_exists_epg_created_message,ap_not_exist_message,tenant_bd_exist_message,tenant_exists_bd_created_message


def demo_start(intent, session):
  print(intent)
  dynamodb = boto3.resource('dynamodb',region_name='us-east-2',aws_access_key_id='AKIA5WJP7OA4QI6D22F2',aws_secret_access_key='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')
  table = dynamodb.Table('apic-details')
  response = table.get_item(
          Key={
              'apic-url':'https://sandboxapicdc.cisco.com/api/',
              }
          )
  url = response['Item']['apic-url']
  username = response['Item']['username']
  password = response['Item']['password']
  tenant_name='avengers_alexa_tenant'
  app_profile='IOT'
  epg1='web'
  epg2='app'
  epg3='db'
  bd1='vlan10'
  bd2='vlan11'
  bd3='vlan12'
  subnet1='10.1.1.1'
  subnet2='10.1.2.1'
  subnet3='10.1.3.1'
  mask='24'
  cookies=aci_login(url,username,password)
  tenant=create_tenant(url,cookies,tenant_name)
  app=create_ap(url,cookies,tenant_name,app_profile)
  create_bd_w_subnet(url,cookies,tenant_name,bd1,subnet1,mask)
  create_bd_w_subnet(url,cookies,tenant_name,bd2,subnet2,mask)
  create_bd_w_subnet(url,cookies,tenant_name,bd3,subnet3,mask)
  create_epg(url,cookies,tenant_name,app_profile,epg1,bd1)
  create_epg(url,cookies,tenant_name,app_profile,epg2,bd2)
  create_epg(url,cookies,tenant_name,app_profile,epg3,bd3)
  demo_done='We have created a new tenant named {} an app profile named {}, three EPGs named {},{} and {} mapped to 3 BDs {},{} and {}'.format(tenant_name,app_profile,epg1,epg2,epg3,bd1,bd2,bd3)
  return get_send_response(demo_done)

def check_bd_exists(url,cookies,tenant_name,bd):
    bd_url_template=Template('node/mo/uni/tn-${tenant_name}/BD-${bd_name}.json')
    bd_url=bd_url_template.substitute(tenant_name=tenant_name,bd_name=bd)
    new_url=url + bd_url
    bd_exists = requests.get(url=new_url,cookies=cookies,verify=False)
    bd_exist=bd_exists.text
    tmp=json.loads(bd_exist)
    if tmp['imdata'] == []:
        return False
    else:
        return True


def create_bd_w_subnet(url,cookies,tenant_name,bd,subnet,mask):
    subnet=subnet + "/" + mask
    bd_url_template=Template('node/mo/uni/tn-${tenant_name}/BD-${bd_name}.json')
    bd_url=bd_url_template.substitute(tenant_name=tenant_name,bd_name=bd)
    new_url=url + bd_url
    print(new_url)
    bd_create_template=Template('{"fvBD":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}","name":"${bd_name}","rn":"BD-${bd_name}","status":"created"},"children":[{"fvSubnet":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}/subnet-[${subnet}]","ctrl":"unspecified","ip":"${subnet}","rn":"subnet-[${subnet}]","status":"created"},"children":[]}},{"fvRsCtx":{"attributes":{"tnFvCtxName":"${tenant_name}","status":"created,modified"},"children":[]}}]}}')
    bd_create=bd_create_template.substitute(tenant_name=tenant_name,bd_name=bd,subnet=subnet)
    print(bd_create)
    new_bd=requests.post(url=new_url,data=bd_create,cookies=cookies,verify=False)
    return new_bd

def bd_start(intent, session):
    print(intent)
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2',aws_access_key_id='AKIA5WJP7OA4QI6D22F2',aws_secret_access_key='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')
    table = dynamodb.Table('apic-details')
    response = table.get_item(
            Key={
                'apic-url':'https://sandboxapicdc.cisco.com/api/',
                }
            )
    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies=aci_login(url,username,password)
    tenant_name=intent['slots']['tenant_name']['value']
    bd=intent['slots']['bd']['value']
    subnet=intent['slots']['subnet']['value']
    mask=intent['slots']['mask']['value']
    #tenant_name='Heroes8'
    #bd='VLAN111'
    #subnet='12.12.12.1/24'

    tenant_exists=check_tenant_exists(url,cookies,tenant_name)
    if tenant_exists == True:
       bd_exists=check_bd_exists(url,cookies,tenant_name,bd)
       if bd_exists == True:
        tenant_bd_exist_msg=tenant_bd_exist_message.format(tenant_name,bd)
        return get_send_response(tenant_bd_exist_msg)
       else:
         response=create_bd_w_subnet(url,cookies,tenant_name,bd,subnet,mask)
         print(response)
         if(response.status_code == 200):
             tenant_exists_bd_created_msg=tenant_exists_bd_created_message.format(tenant_name,bd)
             return get_send_response(tenant_exists_bd_created_msg)
    else:
             tenant_not_exist_msg=tenant_not_exist_message.format(tenant_name)
             return get_send_response(tenant_not_exist_msg)


def check_ap_exists(url,cookies,tenant_name,ap):
    ap_url_template=Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    ap_url=ap_url_template.substitute(tenant_name=tenant_name,ap_name=ap)
    new_url=url + ap_url
    print(new_url)
    ap_exists = requests.get(url=new_url,cookies=cookies,verify=False)
    ap_exist=ap_exists.text
    tmp=json.loads(ap_exist)
    if tmp['imdata'] == []:
        return False
    else:
        return True

def check_epg_exists(url,cookies,tenant_name,ap,epg):
    epg_url_template=Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}/epg-${epg_name}.json')
    epg_url=epg_url_template.substitute(tenant_name=tenant_name,ap_name=ap,epg_name=epg)
    new_url=url + epg_url
    print(new_url)
    epg_exists = requests.get(url=new_url,cookies=cookies,verify=False)
    epg_exist=epg_exists.text
    tmp=json.loads(epg_exist)
    if tmp['imdata'] == []:
        return False
    else:
        return True


def create_epg(url,cookies,tenant_name,ap,epg,bd):
    epg_url_template=Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}/epg-${epg}.json')
    epg_url=epg_url_template.substitute(tenant_name=tenant_name,ap_name=ap,epg=epg)
    new_url=url + epg_url
    epg_create_template=Template('{"fvAEPg":{"attributes":{"dn":"uni/tn-${tenant_name}/ap-${ap}/epg-${epg}","name":"${epg}","rn":"epg-${epg}","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"${bd_name}","status":"created,modified"},"children":[]}}]}}')
    epg_create=epg_create_template.substitute(tenant_name=tenant_name,ap=ap,epg=epg,bd_name=bd)
    new_epg=requests.post(url=new_url,data=epg_create,cookies=cookies,verify=False)
    return new_epg


def epg_start(intent, session):
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2',aws_access_key_id='AKIA5WJP7OA4QI6D22F2',aws_secret_access_key='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')
    table = dynamodb.Table('apic-details')
    response = table.get_item(
            Key={
                'apic-url':'https://sandboxapicdc.cisco.com/api/',
                }
            )
    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies=aci_login(url,username,password)
    tenant_name=intent['slots']['tenant_name']['value']
    ap=intent['slots']['app_profile']['value']
    epg=intent['slots']['epg_name']['value']
    bd=intent['slots']['bd']['value']
    print(tenant_name)
    print(ap)
    print(epg)
    print(bd)
    #tenant_name='Heroes1'
    #ap='Save_The_Planet'
    #epg='web'
    #bd='Hero_Land'
    ap_exists=check_ap_exists(url,cookies,tenant_name,ap)
    if ap_exists == True:
       print('ap exists')
       epg_exists=check_epg_exists(url,cookies,tenant_name,ap,epg)
       if epg_exists == True:
        print('epg exists')
        ap_epg_exist_msg=ap_epg_exist_message.format(ap,epg)
        return get_send_response(ap_epg_exist_msg)
       else:
        print('creatfing epg')
        response=create_epg(url,cookies,tenant_name,ap,epg,bd)
        if(response.status_code == 200):
          ap_exists_epg_created_msg=ap_exists_epg_created_message.format(ap,epg)
          return get_send_response(ap_exists_epg_created_msg)
    else:
          ap_not_exist_msg=ap_not_exist_message.format(tenant_name,ap)
          return get_send_response(ap_not_exist_msg)





def create_snapshot(url,cookies,description):
    snapshot_url='node/mo/uni/fabric/configexp-defaultOneTime.json'
    new_url=url + snapshot_url
    snapshot_payload_template=Template('{\"configExportP\":{\"attributes\":{\"dn\":\"uni/fabric/configexp-defaultOneTime\",\"name\":\"defaultOneTime\",\"snapshot\":\"true\",\"targetDn\":\"\",\"adminSt\":\"triggered\",\"rn\":\"configexp-defaultOneTime\",\"status\":\"created,modified\",\"descr\":\"${descr}\"},\"children\":[]}}')
    snapshot_payload=snapshot_payload_template.substitute(descr=description)
    create_snapshot=requests.post(url=new_url,data=snapshot_payload,cookies=cookies,verify=False)
    return create_snapshot


def snapshot_start(intent, session):
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2',aws_access_key_id='AKIA5WJP7OA4QI6D22F2',aws_secret_access_key='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')
    table = dynamodb.Table('apic-details')
    response = table.get_item(
            Key={
                'apic-url':'https://sandboxapicdc.cisco.com/api/',
                }
            )
    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies=aci_login(url,username,password)
    description=intent['slots']['description']['value']
    response=create_snapshot(url,cookies,description)
    if(response.status_code == 200):
        snapshot_created=snapshot_created_template.format(description)
        return get_send_response(snapshot_created)

    else:
        return get_send_response(snapshot_failed)




def check_ap_exists(url,cookies,tenant_name,ap):
    ap_url_template=Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    ap_url=ap_url_template.substitute(tenant_name=tenant_name,ap_name=ap)
    new_url=url + ap_url
    print(new_url)
    ap_exists = requests.get(url=new_url,cookies=cookies,verify=False)
    ap_exist=ap_exists.text
    tmp=json.loads(ap_exist)
    if tmp['imdata'] == []:
        return False
    else:
        return True


def create_ap(url,cookies,tenant_name,ap):
    ap_url_template=Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    ap_url=ap_url_template.substitute(tenant_name=tenant_name,ap_name=ap)
    new_url=url + ap_url
    ap_create_template=Template('{"fvAp":{"attributes":{"dn":"uni/tn-${tenant_name}/ap-${ap_name}","name":"${ap_name}","rn":"ap-${ap_name}","status":"created"},"children":[]}}')
    ap_create=ap_create_template.substitute(tenant_name=tenant_name,ap_name=ap)
    new_ap=requests.post(url=new_url,data=ap_create,cookies=cookies,verify=False)
    return new_ap

def get_send_response(message):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = message
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, welcome to your custom alexa application!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def app_profile_start(intent, session):
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2',aws_access_key_id='AKIA5WJP7OA4QI6D22F2',aws_secret_access_key='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')
    table = dynamodb.Table('apic-details')
    response = table.get_item(
            Key={
                'apic-url':'https://sandboxapicdc.cisco.com/api/',
                }
            )
    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies=aci_login(url,username,password)
    tenant_name=tenant_name=intent['slots']['tenant_name']['value']
    ap=intent['slots']['app_profile']['value']

    tenant_exists=check_tenant_exists(url,cookies,tenant_name)
    if tenant_exists == True:
       ap_exists=check_ap_exists(url,cookies,tenant_name,ap)
       if ap_exists == True:
        tenant_ap_exist_msg=tenant_ap_exist_message.format(tenant_name,ap)
        return get_send_response(tenant_ap_exist_msg)
       else:
         response=create_ap(url,cookies,tenant_name,ap)
         if(response.status_code == 200):
             tenant_exists_ap_created_msg=tenant_exists_ap_created_message.format(tenant_name,ap)
             return get_send_response(tenant_exists_ap_created_msg)

    else:
             tenant_not_exist_msg=tenant_not_exist_message.format(tenant_name)
             return get_send_response(tenant_not_exist_msg)





def tenant_start(intent,session):
    print(intent)
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2',aws_access_key_id='AKIA5WJP7OA4QI6D22F2',aws_secret_access_key='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')
    table = dynamodb.Table('apic-details')
    response = table.get_item(
            Key={
                'apic-url':'https://sandboxapicdc.cisco.com/api/',
                }
            )
    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    tenant_name=intent['slots']['tenant_name']['value']
    print(tenant_name)
    #tenant_name='zeeeus'
    cookies=aci_login(url,username,password)
    #slots = event['currentIntent']['slots']


    tenant_exists=check_tenant_exists(url,cookies,tenant_name)
    print(tenant_exists)

    if tenant_exists == True:
        tenant_exists_msg=tenant_exists_message.format(tenant_name)
        return get_send_response(tenant_exists_msg)
    else:
        response=create_tenant(url,cookies,tenant_name)
        print(response.status_code)
        if(response.status_code == 200):
            tenant_created_msg=tenant_created_message.format(tenant_name)
            return get_send_response(tenant_created_msg)
        else:
            tenant_failed_msg=tenant_failed_message.format(tenant_name)
            return get_send_response(tenant_failed_msg)



# --------------- Helpers that build all of the responses ----------------------

def check_tenant_exists(url,cookies,tenant_name):
    tenant_url_template=Template('node/mo/uni/tn-${tenant_name}.json')
    tenant_url=tenant_url_template.substitute(tenant_name=tenant_name)
    new_url=url + tenant_url
    tenant_exists = requests.get(url=new_url,cookies=cookies,verify=False)
    tenant_exist=tenant_exists.text
    tmp=json.loads(tenant_exist)
    if tmp['imdata'] == []:
        return False
    else:
        return True


def create_tenant(url,cookies,tenant_name):
    print(cookies)
    tenant_url_template=Template('node/mo/uni/tn-${tenant_name}.json')
    tenant_url=tenant_url_template.substitute(tenant_name=tenant_name)
    new_url=url + tenant_url
    tenant_create_template=Template('{"fvTenant":{"attributes":{"dn":"uni/tn-${tenant_name}","name":"${tenant_name}","rn":"tn-${tenant_name}","status":"created"},"children":[{"fvCtx":{"attributes":{"dn":"uni/tn-${tenant_name}/ctx-${tenant_name}","name":"${tenant_name}","rn":"ctx-${tenant_name}","status":"created"},"children":[]}}]}}')
    tenant_create=tenant_create_template.substitute(tenant_name=tenant_name)
    print(tenant_create)
    new_tenant=requests.post(url=new_url,data=tenant_create,cookies=cookies,verify=False)
    print(new_tenant)
    return new_tenant




def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
def get_compliment_response():
    """ An example of a custom intent. Same structure as welcome message, just make sure to add this intent
    in your alexa skill in order for it to work.
    """
    session_attributes = {}
    card_title = "Compliment"
    compliment='you are really nice'
    speech_output = compliment
    reprompt_text = "I said," + compliment
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_insult_response(intent,session):
    """ An example of a custom intent. Same structure as welcome message, just make sure to add this intent
    in your alexa skill in order for it to work.
    """
    print(intent)
    session_attributes = {}
    name=intent['slots']['name']['value']
    print(name)
    card_title = "Insult"
    speech_output = "{} is a dog".format(name)
    reprompt_text = "I would rather not do that."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "What up what up what up, your application has started!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, welcome to your custom alexa application!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass



def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print(intent_name)
    # Dispatch to your skill's intent handlers
    if intent_name == "compliment":
        return get_compliment_response()
    if intent_name == "demo":
        return demo_start(intent,session)
    if intent_name == "ap_profile":
        return app_profile_start(intent, session)
    elif intent_name == "insult":
        return get_insult_response(intent,session)
    elif intent_name == "tenant":
        return tenant_start(intent,session)
    elif intent_name == "epg":
        return epg_start(intent,session)
    elif intent_name == "create_bd":
        return bd_start(intent,session)
    elif intent_name == "snapshot":
        return snapshot_start(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")
    print(event)
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
