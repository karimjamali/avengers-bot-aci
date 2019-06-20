import json
from string import Template
from messages import *
from utils import *


def check_tenant_exists(url,cookies,tenant_name):

    full_url = "{}node/mo/uni/tn-{}.json".format(url,tenant_name)

    tenant_exists_response = make_get_api_call(full_url,cookies=cookies)
    json_data = json.loads(tenant_exists_response.text)

    if json_data['imdata'] == []:
        return False
    else:
        return True


def create_tenant(url,cookies,tenant_name):
    print(cookies)

    full_url = "{}node/mo/uni/tn-{}.json".format(url,tenant_name)

    payload_template = Template('{"fvTenant":{"attributes":{"dn":"uni/tn-${tenant_name}","name":"${tenant_name}","rn":"tn-${tenant_name}","status":"created"},"children":[{"fvCtx":{"attributes":{"dn":"uni/tn-${tenant_name}/ctx-${tenant_name}","name":"${tenant_name}","rn":"ctx-${tenant_name}","status":"created"},"children":[]}}]}}')

    payload_data = payload_template.substitute(tenant_name=tenant_name)
    print(payload_data)

    new_tenant = make_post_api_call(full_url,payload=payload_data,cookies=cookies)
    print(new_tenant)

    return new_tenant


def tenant_handler(event, context):
    #Get the url,username,and password from session attributes & tenant_name from slots input, login to APIC, check tenant ap_exists
    #create new tenant if required

    print(event)

    url=event['sessionAttributes']['url']
    username=event['sessionAttributes']['username']
    password=event['sessionAttributes']['password']

    tenant_name=event['currentIntent']['slots']['tenant_name']

    print(tenant_name)
    #tenant_name='zeeeus'

    cookies = aci_login(url, username, password)
    #slots = event['currentIntent']['slots']

    tenant_exists = check_tenant_exists(url, cookies, tenant_name)
    print(tenant_exists)

    if tenant_exists == True:
        tenant = "**{}**".format(tenant_name)
        tenant_exists_msg = tenant_exists_message.format(tenant)

        intent_fulfilled_exist = generate_response_code(event, "SKIP",
                                                  dialog_type="CLOSEFULLFILLED",
                                                  fulfill_state="Fulfilled",
                                                  message=tenant_exists_msg)

        # intent_fulfilled= {
        #     "dialogAction": {
        #     "type": "Close",
        #     "fulfillmentState": "Fulfilled",
        #     "message": {"contentType": "PlainText","content": tenant_exists_msg }
        #     }
        #     }
        return intent_fulfilled_exist
    else:
        response=create_tenant(url,cookies,tenant_name)
        print(response.status_code)
        if response.status_code == 200:
            tenant = "**{}**".format(tenant_name)
            tenant_created_msg=tenant_created_message.format(tenant)

            intent_fulfilled = generate_response_code(event, "SKIP",
                                                      dialog_type="CLOSEFULLFILLED",
                                                      fulfill_state="Fulfilled",
                                                      message=tenant_created_msg)
            return intent_fulfilled

            # intent_fulfilled = {
            #     "dialogAction": {
            #         "type": "Close",
            #         "fulfillmentState": "Fulfilled",
            #         "message": {"contentType": "PlainText","content": tenant_created_msg }
            #         }
            #     }
        else:
            tenant = "**{}**".format(tenant_name)
            tenant_failed_msg=tenant_failed_message.format(tenant)

            intent_failed = generate_response_code(event, "SKIP",
                                                   dialog_type="CLOSEFAILED",
                                                   fulfill_state="Fulfilled",
                                                   message=tenant_failed_msg)
            return intent_failed

            # intent_failed = {
            #     "dialogAction": {
            #     "type": "Close",
            #     "fulfillmentState": "Failed",
            #     "message": {"contentType": "PlainText","content": tenant_failed_msg }
            #     }
            #     }
