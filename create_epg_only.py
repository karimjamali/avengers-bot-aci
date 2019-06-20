import json
from string import Template
from messages import ap_epg_exist_message, ap_exists_epg_created_message, ap_not_exist_message
from utils import aci_login, generate_response_code, make_post_api_call, make_get_api_call


def check_ap_exists(base_url, cookies, tenant_name, ap):
    # ap_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    # ap_url = ap_url_template.substitute(tenant_name=tenant_name, ap_name=ap)
    # new_url = url + ap_url

    ap_url_full = '{}node/mo/uni/tn-{}/ap-{}.json'.format(base_url,tenant_name,ap)
    ap_exists = make_get_api_call(ap_url_full, cookies=cookies)

    json_data = json.loads(ap_exists.text)
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
    return new_epg


def epg_handler(event, context):
    # Get the url,username,and password from session attributes
    print(event)

    url = event['sessionAttributes']['url']
    username = event['sessionAttributes']['username']
    password = event['sessionAttributes']['password']

    cookies = aci_login(url, username, password)

    slots = event['currentIntent']['slots']
    tenant_name = event['currentIntent']['slots']['tenant_name']
    ap = event['currentIntent']['slots']['app_profile']
    epg = event['currentIntent']['slots']['epg']
    bd = event['currentIntent']['slots']['bd']

    ap_exists = check_ap_exists(url, cookies, tenant_name, ap)

    if ap_exists == True:
        epg_exists = check_epg_exists(url, cookies, tenant_name, ap, epg)
        if epg_exists == True:
            ap_epg_exist_msg = ap_epg_exist_message.format(ap, epg)

            both_ap_epg_exist = generate_response_code(event,"SKIP",
                                                       dialog_type="CLOSEFULLFILLED",
                                                       message=ap_epg_exist_msg)
            # both_ap_epg_exist = {
            #     "dialogAction": {
            #         "type": "Close",
            #         "fulfillmentState": "Fulfilled",
            #         "message": {"contentType": "PlainText", "content": ap_epg_exist_msg}
            #     }
            # }
            print(ap_epg_exist_msg)
            return both_ap_epg_exist
        else:
            response = create_epg(url, cookies, tenant_name, ap, epg, bd)
            print(response)
            if response.status_code == 200:
                ap_exists_epg_created_msg = ap_exists_epg_created_message.format(ap, epg)

                ap_exists_epg_created = generate_response_code(event,"SKIP",
                                                               dialog_type="CLOSEFULLFILLED",
                                                               message=ap_exists_epg_created_msg)
                # ap_exists_epg_created = {
                #     "dialogAction": {
                #         "type": "Close",
                #         "fulfillmentState": "Fulfilled",
                #         "message": {"contentType": "PlainText", "content": ap_exists_epg_created_msg}
                #     }
                # }
                print(ap_exists_epg_created_msg)
                return ap_exists_epg_created
    else:
        ap_not_exist_msg = ap_not_exist_message.format(tenant_name, ap)
        ap_not_exist = generate_response_code(event,"SKIP",
                                              dialog_type="CLOSEFULLFILLED",
                                              message=ap_not_exist_msg)
        # ap_not_exist = {
        #     "dialogAction": {
        #         "type": "Close",
        #         "fulfillmentState": "Failed",
        #         "message": {"contentType": "PlainText", "content": ap_not_exist_msg}
        #     }
        # }
        print(ap_not_exist_msg)
        return ap_not_exist


if __name__ == "__main__":
    epg_handler('event', 'context')
