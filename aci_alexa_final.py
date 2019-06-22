"""
AWS lambda code by end of part 2 of programming alexa series
"""

from __future__ import print_function
import boto3
import json
from string import Template
from messages import *
from utils import get_logindata_from_ddb, aci_login, make_get_api_call, make_post_api_call
from demo_alexa_config_parameters import *

def demo_start(intent, session):
    print(intent)

    response = get_logindata_from_ddb()

    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']


    cookies = aci_login(url, username, password)
    tenant = create_tenant(url, cookies, tenant_name)
    app = create_ap(url, cookies, tenant_name, app_profile)
    create_bd_w_subnet(url, cookies, tenant_name, bd1, subnet1, mask)
    create_bd_w_subnet(url, cookies, tenant_name, bd2, subnet2, mask)
    create_bd_w_subnet(url, cookies, tenant_name, bd3, subnet3, mask)
    create_epg(url, cookies, tenant_name, app_profile, epg1, bd1)
    create_epg(url, cookies, tenant_name, app_profile, epg2, bd2)
    create_epg(url, cookies, tenant_name, app_profile, epg3, bd3)
    demo_done = 'We have created a new tenant named {} an app profile named {}, three EPGs named {},{} and {} mapped to 3 BDs {},{} and {}'.format(
        tenant_name, app_profile, epg1, epg2, epg3, bd1, bd2, bd3)
    return get_send_response(demo_done)


def check_bd_exists(base_url, cookies, tenant_name, bd):
    # bd_url_template = Template('node/mo/uni/tn-${tenant_name}/BD-${bd_name}.json')
    # bd_url = bd_url_template.substitute(tenant_name=tenant_name, bd_name=bd)
    # new_url = url + bd_url
    #
    # bd_exists = requests.get(url=new_url, cookies=cookies, verify=False)

    bd_url_full = '{}node/mo/uni/tn-{}/BD-{}.json'.format(base_url, tenant_name, bd)
    bd_exist = make_get_api_call(bd_url_full, cookies=cookies)
    json_data = json.loads(bd_exist.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True



def create_bd_w_subnet(base_url, cookies, tenant_name, bd, subnet,mask):
    # bd_url_template = Template('node/mo/uni/tn-${tenant_name}/BD-${bd_name}.json')
    # bd_url = bd_url_template.substitute(tenant_name=tenant_name, bd_name=bd)
    # new_url = url + bd_url
    # new_bd = requests.post(url=bd_url_full, data=bd_create, cookies=cookies, verify=False)
    subnet="{}/{}".format(subnet,mask)
    bd_url_full = '{}node/mo/uni/tn-{}/BD-{}.json'.format(base_url, tenant_name, bd)

    bd_create_template = Template(
        '{"fvBD":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}","name":"${bd_name}","rn":"BD-${bd_name}","status":"created"},"children":[{"fvSubnet":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}/subnet-[${subnet}]","ctrl":"unspecified","ip":"${subnet}","rn":"subnet-[${subnet}]","status":"created"},"children":[]}},{"fvRsCtx":{"attributes":{"tnFvCtxName":"${tenant_name}","status":"created,modified"},"children":[]}}]}}')
    bd_create = bd_create_template.substitute(tenant_name=tenant_name, bd_name=bd, subnet=subnet)

    new_bd = make_post_api_call(bd_url_full, payload=bd_create, cookies=cookies)

    return new_bd


def bd_start(intent, session):
    print(intent)

    response = get_logindata_from_ddb()

    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies = aci_login(url, username, password)

    tenant_name = intent['slots']['tenant_name']['value']
    bd = intent['slots']['bd']['value']
    subnet = intent['slots']['subnet']['value']
    mask = intent['slots']['mask']['value']
    # tenant_name='Heroes8'
    # bd='VLAN111'
    # subnet='12.12.12.1/24'
    
    tenant_exists = check_tenant_exists(url, cookies, tenant_name)
    if tenant_exists:
        bd_exists = check_bd_exists(url, cookies, tenant_name, bd)
        if bd_exists:
            tenant_bd_exist_msg = tenant_bd_exist_message.format(tenant_name, bd)
            return get_send_response(tenant_bd_exist_msg)
        else:
            response = create_bd_w_subnet(url, cookies, tenant_name, bd, subnet, mask)
            print(response)
            if response.status_code == 200:
                tenant_exists_bd_created_msg = tenant_exists_bd_created_message.format(tenant_name, bd)
                return get_send_response(tenant_exists_bd_created_msg)
    else:
        tenant_not_exist_msg = tenant_not_exist_message.format(tenant_name)
        return get_send_response(tenant_not_exist_msg)


def check_ap_exists(base_url, cookies, tenant_name, ap_name):
    # ap_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    # ap_url = ap_url_template.substitute(tenant_name=tenant_name, ap_name=ap)
    # new_url = url + ap_url

    # ap_exists = requests.get(url=new_url, cookies=cookies, verify=False)
    # ap_exist = ap_exists.text

    ap_url_full = '{}node/mo/uni/tn-{}/ap-{}.json'.format(base_url,tenant_name,ap_name)
    print(ap_url_full)
    ap_exist_response = make_get_api_call(ap_url_full, cookies=cookies)

    json_data = json.loads(ap_exist_response.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


def check_epg_exists(base_url, cookies, tenant_name, ap, epg):
    # epg_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}/epg-${epg_name}.json')
    # epg_url = epg_url_template.substitute(tenant_name=tenant_name, ap_name=ap, epg_name=epg)
    # new_url = url + epg_url
    epg_url_template_full = '{}node/mo/uni/tn-{}/ap-{}/epg-{}.json'.format(base_url,tenant_name,ap,epg)
    print(epg_url_template_full)
    epg_exists = make_get_api_call(epg_url_template_full, cookies=cookies)

    json_data = json.loads(epg_exists.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


def create_epg(base_url, cookies, tenant_name, ap, epg, bd):
    # epg_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}/epg-${epg}.json')
    # epg_url = epg_url_template.substitute(tenant_name=tenant_name, ap_name=ap, epg=epg)
    # new_url = url + epg_url
    epg_url_template_full = '{}node/mo/uni/tn-{}/ap-{}/epg-{}.json'.format(base_url, tenant_name, ap, epg)

    epg_create_template = Template('{"fvAEPg":{"attributes":{"dn":"uni/tn-${tenant_name}/ap-${ap}/epg-${epg}","name":"${epg}","rn":"epg-${epg}","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"${bd_name}","status":"created,modified"},"children":[]}}]}}')
    epg_create = epg_create_template.substitute(tenant_name=tenant_name, ap=ap, epg=epg, bd_name=bd)

    new_epg = make_post_api_call(epg_url_template_full, payload=epg_create, cookies=cookies)
    return epg_url_template_full


def epg_start(intent, session):
    response = get_logindata_from_ddb()

    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies = aci_login(url, username, password)
    tenant_name = intent['slots']['tenant_name']['value']
    ap = intent['slots']['app_profile']['value']
    epg = intent['slots']['epg_name']['value']
    bd = intent['slots']['bd']['value']
    print(tenant_name)
    print(ap)
    print(epg)
    print(bd)
    # tenant_name='Heroes1'
    # ap='Save_The_Planet'
    # epg='web'
    # bd='Hero_Land'
    ap_exists = check_ap_exists(url, cookies, tenant_name, ap)
    if ap_exists:
        print('ap exists')
        epg_exists = check_epg_exists(url, cookies, tenant_name, ap, epg)
        if epg_exists:
            print('epg exists')
            ap_epg_exist_msg = ap_epg_exist_message.format(ap, epg)
            return get_send_response(ap_epg_exist_msg)
        else:
            print('creatfing epg')
            response = create_epg(url, cookies, tenant_name, ap, epg, bd)
            if response.status_code == 200:
                ap_exists_epg_created_msg = ap_exists_epg_created_message.format(ap, epg)
                return get_send_response(ap_exists_epg_created_msg)
    else:
        ap_not_exist_msg = ap_not_exist_message.format(tenant_name, ap)
        return get_send_response(ap_not_exist_msg)


def create_snapshot(base_url, cookies, description):
    snapshot_url = '{}node/mo/uni/fabric/configexp-defaultOneTime.json'.format(base_url)
    snapshot_payload_template = Template(
        '{\"configExportP\":{\"attributes\":{\"dn\":\"uni/fabric/configexp-defaultOneTime\",\"name\":\"defaultOneTime\",\"snapshot\":\"true\",\"targetDn\":\"\",\"adminSt\":\"triggered\",\"rn\":\"configexp-defaultOneTime\",\"status\":\"created,modified\",\"descr\":\"${descr}\"},\"children\":[]}}')
    snapshot_payload = snapshot_payload_template.substitute(descr=description)

    create_snapshot = make_post_api_call(snapshot_url, payload=snapshot_payload, cookies=cookies)
    return create_snapshot


def snapshot_start(intent, session):

    response = get_logindata_from_ddb()

    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies = aci_login(url, username, password)
    description = intent['slots']['description']['value']
    response = create_snapshot(url, cookies, description)
    if response.status_code == 200:
        snapshot_created = snapshot_created_template.format(description)
        return get_send_response(snapshot_created)

    else:
        return get_send_response(snapshot_failed)


def create_ap(base_url, cookies, tenant_name, ap_name):
    # ap_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    # ap_url = ap_url_template.substitute(tenant_name=tenant_name, ap_name=ap)
    # new_url = url + ap_url
    # new_ap = requests.post(url=new_url, data=ap_create, cookies=cookies, verify=False)

    ap_url_full = '{}node/mo/uni/tn-{}/ap-{}.json'.format(base_url,tenant_name,ap_name)
    print(ap_url_full)

    ap_create_template = Template('{"fvAp":{"attributes":{"dn":"uni/tn-${tenant_name}/ap-${ap_name}","name":"${ap_name}","rn":"ap-${ap_name}","status":"created"},"children":[]}}')
    ap_create_data_payload = ap_create_template.substitute(tenant_name=tenant_name, ap_name=ap_name)

    ap_response =  make_post_api_call(ap_url_full,payload=ap_create_data_payload,cookies=cookies)
    return ap_response


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
    response = get_logindata_from_ddb()

    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    cookies = aci_login(url, username, password)
    tenant_name = tenant_name = intent['slots']['tenant_name']['value']
    ap = intent['slots']['app_profile']['value']

    tenant_exists = check_tenant_exists(url, cookies, tenant_name)
    if tenant_exists:
        ap_exists = check_ap_exists(url, cookies, tenant_name, ap)
        if ap_exists:
            tenant_ap_exist_msg = tenant_ap_exist_message.format(tenant_name, ap)
            return get_send_response(tenant_ap_exist_msg)
        else:
            response = create_ap(url, cookies, tenant_name, ap)
            if response.status_code == 200:
                tenant_exists_ap_created_msg = tenant_exists_ap_created_message.format(tenant_name, ap)
                return get_send_response(tenant_exists_ap_created_msg)

    else:
        tenant_not_exist_msg = tenant_not_exist_message.format(tenant_name)
        return get_send_response(tenant_not_exist_msg)


def tenant_start(intent, session):
    response = get_logindata_from_ddb()
    url = response['Item']['apic-url']
    username = response['Item']['username']
    password = response['Item']['password']

    tenant_name = intent['slots']['tenant_name']['value']
    print(tenant_name)
    # tenant_name='zeeeus'
    cookies = aci_login(url, username, password)
    # slots = event['currentIntent']['slots']

    tenant_exists = check_tenant_exists(url, cookies, tenant_name)
    print(tenant_exists)

    if tenant_exists:
        tenant_exists_msg = tenant_exists_message.format(tenant_name)
        return get_send_response(tenant_exists_msg)
    else:
        response = create_tenant(url, cookies, tenant_name)
        print(response.status_code)
        if response.status_code == 200:
            tenant_created_msg = tenant_created_message.format(tenant_name)
            return get_send_response(tenant_created_msg)
        else:
            tenant_failed_msg = tenant_failed_message.format(tenant_name)
            return get_send_response(tenant_failed_msg)


# --------------- Helpers that build all of the responses ----------------------

def check_tenant_exists(base_url, cookies, tenant_name):
    tenant_full_url = '{}node/mo/uni/tn-{}.json'.format(base_url, tenant_name)
    print(tenant_full_url)
    tenant_exist_response = make_get_api_call(tenant_full_url, cookies=cookies)

    json_data = json.loads(tenant_exist_response.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


def create_tenant(base_url, cookies, tenant_name):
    tenant_url_full = '{}node/mo/uni/tn-{}.json'.format(base_url, tenant_name)
    print(tenant_url_full)
    tenant_create_template = Template('{"fvTenant":{"attributes":{"dn":"uni/tn-${tenant_name}","name":"${tenant_name}","rn":"tn-${tenant_name}","status":"created"},"children":[{"fvCtx":{"attributes":{"dn":"uni/tn-${tenant_name}/ctx-${tenant_name}","name":"${tenant_name}","rn":"ctx-${tenant_name}","status":"created"},"children":[]}}]}}')
    tenant_create_payload_data = tenant_create_template.substitute(tenant_name=tenant_name)

    new_tenant_reponse = make_post_api_call(tenant_url_full, payload=tenant_create_payload_data, cookies=cookies)
    return new_tenant_reponse


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
    compliment = 'you are really nice'
    speech_output = compliment
    reprompt_text = "I said," + compliment
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_insult_response(intent, session):
    """ An example of a custom intent. Same structure as welcome message, just make sure to add this intent
    in your alexa skill in order for it to work.
    """
    print(intent)
    session_attributes = {}
    name = intent['slots']['name']['value']
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
    speech_output = "Welcome to the ACI Avengers alexa skill, a simple skill whose objective is to interact with Cisco Application Centric Infrastructure"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, welcome to your custom alexa application!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the ACI Avengers Alexa Skill. " \
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

    if intent_name == "demo":
        return demo_start(intent, session)
    if intent_name == "ap_profile":
        return app_profile_start(intent, session)
    elif intent_name == "insult":
        return get_insult_response(intent, session)
    elif intent_name == "tenant":
        return tenant_start(intent, session)
    elif intent_name == "epg":
        return epg_start(intent, session)
    elif intent_name == "create_bd":
        return bd_start(intent, session)
    elif intent_name == "snapshot":
        return snapshot_start(intent, session)
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
