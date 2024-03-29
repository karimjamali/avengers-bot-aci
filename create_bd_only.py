import json
from string import Template
from messages import tenant_bd_exist_message,tenant_exists_bd_created_message,tenant_not_exist_message,not_logged_in
from utils import make_get_api_call, make_post_api_call, generate_response_code, aci_login,validate_if_logged_in


def check_bd_exists(base_url, cookies, tenant_name, bd):
    bd_url_full = '{}node/mo/uni/tn-{}/BD-{}.json'.format(base_url, tenant_name, bd)
    bd_exist = make_get_api_call(bd_url_full, cookies=cookies)
    json_data = json.loads(bd_exist.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


def check_tenant_exists(base_url, cookies, tenant_name):
    tenant_url_full = '{}node/mo/uni/tn-{}.json'.format(base_url, tenant_name)
    tenant_exist = make_get_api_call(tenant_url_full, cookies=cookies)

    json_data = json.loads(tenant_exist.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


def create_bd_w_subnet(base_url, cookies, tenant_name, bd, subnet):
    bd_url_full = '{}node/mo/uni/tn-{}/BD-{}.json'.format(base_url, tenant_name, bd)

    bd_create_template = Template(
        '{"fvBD":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}","name":"${bd_name}","rn":"BD-${bd_name}","status":"created"},"children":[{"fvSubnet":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}/subnet-[${subnet}]","ctrl":"unspecified","ip":"${subnet}","rn":"subnet-[${subnet}]","status":"created"},"children":[]}},{"fvRsCtx":{"attributes":{"tnFvCtxName":"${tenant_name}","status":"created,modified"},"children":[]}}]}}')
    bd_create = bd_create_template.substitute(tenant_name=tenant_name, bd_name=bd, subnet=subnet)

    new_bd = make_post_api_call(bd_url_full, payload=bd_create, cookies=cookies)

    return new_bd

def bd_handler(event, context):
    #Get the url,username,and password from session attributes
    print(event)
    if not validate_if_logged_in(event):
        return generate_response_code(event,"SKIP",dialog_type="ELICIT", message=not_logged_in)
    url = event['sessionAttributes']['url']
    username = event['sessionAttributes']['username']
    password = event['sessionAttributes']['password']

    cookies = aci_login(url, username, password)

    slots = event['currentIntent']['slots']
    tenant_name = event['currentIntent']['slots']['tenant_name']
    bd = event['currentIntent']['slots']['bd']

    subnet = event['currentIntent']['slots']['subnet']

    tenant_exists=check_tenant_exists(url,cookies,tenant_name)
    if tenant_exists == True:
       bd_exists=check_bd_exists(url,cookies,tenant_name,bd)
       if bd_exists == True:
        tenant_bd_exist_msg=tenant_bd_exist_message.format(tenant_name,bd)
        both_tenant_bd_exist = generate_response_code(event, "SKIP",
                                                      dialog_type="CLOSEFULLFILLED",
                                                      message=tenant_bd_exist_msg)
        print(tenant_bd_exist_msg)
        return both_tenant_bd_exist


       else:
         response=create_bd_w_subnet(url,cookies,tenant_name,bd,subnet)
         print(response)
         if response.status_code == 200:
             tenant_exists_bd_created_msg=tenant_exists_bd_created_message.format(tenant_name, bd)
             tenant_exists_bd_created = generate_response_code(event, "SKIP",
                                                               dialog_type="CLOSEFULLFILLED",
                                                               message=tenant_exists_bd_created_msg
                                                               )
             print(tenant_exists_bd_created_msg)
             return tenant_exists_bd_created


    else:
             tenant_not_exist_msg=tenant_not_exist_message.format(tenant_name)

             tenant_not_exist = generate_response_code(event, "SKIP",
                                                       dialog_type="CLOSEFULLFILLED",
                                                       message=tenant_not_exist_msg)
             print(tenant_not_exist_msg)
             return tenant_not_exist




if __name__ == "__main__":
    bd_handler('event', 'context')
