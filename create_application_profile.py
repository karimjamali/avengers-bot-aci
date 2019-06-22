import json
from string import Template
from messages import tenant_ap_exist_message,tenant_exists_ap_created_message,tenant_not_exist_message,error_create_app_profile_message,not_logged_in
from utils import make_get_api_call, make_post_api_call, aci_login, generate_response_code,validate_if_logged_in


def check_tenant_exists(base_url, cookies, tenant_name):
    # tenant_url_template=Template('node/mo/uni/tn-${tenant_name}.json')
    # tenant_url = tenant_url_template.substitute(tenant_name=tenant_name)
    # new_url = url + tenant_url
    # tenant_exists = requests.get(url=new_url, cookies=cookies, verify=False)

    tenant_full_url = '{}node/mo/uni/tn-{}.json'.format(base_url, tenant_name)
    print(tenant_full_url)
    tenant_exist_response = make_get_api_call(tenant_full_url, cookies=cookies)

    json_data = json.loads(tenant_exist_response.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


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



def create_tenant(base_url, cookies, tenant_name):
    # tenant_url_template = Template('node/mo/uni/tn-${tenant_name}.json')
    # tenant_url = tenant_url_template.substitute(tenant_name=tenant_name)
    # new_url = url + tenant_url
    # tenant_url = tenant_url_template.substitute(tenant_name=tenant_name)
    # new_tenant = requests.post(url=tenant_url_full, data=tenant_create_payload_data, cookies=cookies, verify=False)

    tenant_url_full = '{}node/mo/uni/tn-{}.json'.format(base_url, tenant_name)
    print(tenant_url_full)
    tenant_create_template = Template('{"fvTenant":{"attributes":{"dn":"uni/tn-${tenant_name}","name":"${tenant_name}","rn":"tn-${tenant_name}","status":"created"},"children":[{"fvCtx":{"attributes":{"dn":"uni/tn-${tenant_name}/ctx-${tenant_name}","name":"${tenant_name}","rn":"ctx-${tenant_name}","status":"created"},"children":[]}}]}}')
    tenant_create_payload_data = tenant_create_template.substitute(tenant_name=tenant_name)

    new_tenant_reponse = make_post_api_call(tenant_url_full, payload=tenant_create_payload_data, cookies=cookies)
    return new_tenant_reponse


def app_profile_handler(event, context):
    #Get the url,username,and password from session attributes
    print(event)

    if not validate_if_logged_in(event):
        return generate_response_code(event,"SKIP",dialog_type="ELICIT",
                                      message=not_logged_in)
    url = event['sessionAttributes']['url']
    username = event['sessionAttributes']['username']
    password = event['sessionAttributes']['password']


    cookies=aci_login(url,username,password)

    slots = event['currentIntent']['slots']
    tenant_name = event['currentIntent']['slots']['tenant_name']

    ap = event['currentIntent']['slots']['app_profile']

    tenant_exists = check_tenant_exists(url, cookies, tenant_name)

    if tenant_exists == True:
       ap_exists=check_ap_exists(url,cookies,tenant_name,ap)
       if ap_exists == True:
        tenant_ap_exist_msg=tenant_ap_exist_message.format(tenant_name,ap)
        both_tenant_ap_exist = generate_response_code(event, "SKIP",
                                                      dialog_type="CLOSEFULLFILLED",
                                                      message=tenant_ap_exist_msg)
        print(tenant_ap_exist_msg)
        return both_tenant_ap_exist

        # both_tenant_ap_exist= {
        #     "dialogAction": {
        #     "type": "Close",
        #     "fulfillmentState": "Fulfilled",
        #     "message": {"contentType": "PlainText","content": tenant_ap_exist_msg }
        #         }
        #     }
        # print(tenant_ap_exist_msg)
        # return both_tenant_ap_exist
       else:
         response=create_ap(url,cookies,tenant_name,ap)
         print(response)
         try:
            if response.status_code == 200:
                tenant_exists_ap_created_msg=tenant_exists_ap_created_message.format(tenant_name,ap)
                tenant_exists_ap_created = generate_response_code(event, "SKIP",
                                                               dialog_type="CLOSEFULLFILLED",
                                                               message=tenant_exists_ap_created_msg)
                print(tenant_exists_ap_created_msg)
                return tenant_exists_ap_created

         except:
            error_create_app_profile_msg=error_create_app_profile_message.format(ap,tenant_name)
            error_create_app_profile= generate_response_code(event, "SKIP",
                                                               dialog_type="CLOSEFULLFILLED",
                                                               message=error_create_app_profile_msg)


    else:
             tenant_not_exist_msg=tenant_not_exist_message.format(tenant_name)
             tenant_not_exist = generate_response_code(event, "SKIP",
                                                       dialog_type="CLOSEFAILED",
                                                       message=tenant_not_exist_msg)
             print(tenant_not_exist_msg)
             return tenant_not_exist

             # tenant_not_exist = {
             #     "dialogAction": {
             #     "type": "Close",
             #     "fulfillmentState": "Failed",
             #     "message": {"contentType": "PlainText","content": tenant_not_exist_msg }
             #     }
             #     }
             # print(tenant_not_exist_msg)
             # return tenant_not_exist



if __name__ == "__main__":
    app_profile_handler('event', 'context')
