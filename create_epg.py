import json
import re
from string import Template
from utils import make_get_api_call, make_post_api_call, generate_response_code, get_logindata_from_ddb, aci_login


def check_tenant_exists(base_url, cookies, tenant_name):
    # tenant_url_template=Template('node/mo/uni/tn-${tenant_name}.json')
    # tenant_url=tenant_url_template.substitute(tenant_name=tenant_name)
    # new_url=url + tenant_url

    tenant_url_full = '{}node/mo/uni/tn-{}.json'.format(base_url, tenant_name)
    tenant_exists = make_get_api_call(tenant_url_full, cookies=cookies)

    json_data = json.loads(tenant_exists.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


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


def create_ap(base_url, cookies, tenant_name, ap_name):
    # ap_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}.json')
    # ap_url = ap_url_template.substitute(tenant_name=tenant_name, ap_name=ap)
    # new_url = url + ap_url
    # new_ap = requests.post(url=new_url, data=ap_create, cookies=cookies, verify=False)

    ap_url_full = '{}node/mo/uni/tn-{}/ap-{}.json'.format(base_url,tenant_name,ap_name)
    print(ap_url_full)

    ap_create_template = Template(
        '{"fvAp":{"attributes":{"dn":"uni/tn-${tenant_name}/ap-${ap_name}","name":"${ap_name}","rn":"ap-${ap_name}","status":"created"},"children":[]}}')
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
    tenant_create_template = Template(
        '{"fvTenant":{"attributes":{"dn":"uni/tn-${tenant_name}","name":"${tenant_name}","rn":"tn-${tenant_name}","status":"created"},"children":[{"fvCtx":{"attributes":{"dn":"uni/tn-${tenant_name}/ctx-${tenant_name}","name":"${tenant_name}","rn":"ctx-${tenant_name}","status":"created"},"children":[]}}]}}')
    tenant_create_payload_data = tenant_create_template.substitute(tenant_name=tenant_name)

    new_tenant_reponse = make_post_api_call(tenant_url_full, payload=tenant_create_payload_data, cookies=cookies)
    return new_tenant_reponse


def create_bd_w_subnet(base_url, cookies, tenant_name, bd, subnet):
    # bd_url_template = Template('node/mo/uni/tn-${tenant_name}/BD-${bd_name}.json')
    # bd_url = bd_url_template.substitute(tenant_name=tenant_name, bd_name=bd)
    # new_url = url + bd_url

    bd_url_template_full = '{}node/mo/uni/tn-{}/BD-{}.json'.format(base_url,tenant_name,bd)
    print(bd_url_template_full)
    bd_create_template = Template('{"fvBD":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}","name":"${bd_name}","rn":"BD-${bd_name}","status":"created"},"children":[{"fvSubnet":{"attributes":{"dn":"uni/tn-${tenant_name}/BD-${bd_name}/subnet-[${subnet}]","ctrl":"unspecified","ip":"${subnet}","rn":"subnet-[${subnet}]","status":"created"},"children":[]}},{"fvRsCtx":{"attributes":{"tnFvCtxName":"${tenant_name}","status":"created,modified"},"children":[]}}]}}')
    bd_create = bd_create_template.substitute(tenant_name=tenant_name, bd_name=bd, subnet=subnet)
    print(bd_create)
    print('creating bd')
    new_bd = make_post_api_call(bd_url_template_full, payload=bd_create, cookies=cookies)
    print('created bd')
    return bd_url_template_full


def bind_epg_to_interface(epg_url, cookies, vlan_id, leaf, port):

    bind_to_interface_template = Template('{"fvRsPathAtt":{"attributes":{"encap":"vlan-${vlan_id}","instrImedcy":"immediate","tDn":"topology/pod-1/paths-${leaf}/pathep-[${port}]","status":"created"},"children":[]}})')
    bind_to_interface=bind_to_interface_template.substitute(vlan_id=vlan_id,leaf=leaf,port=port)

    response = make_post_api_call(epg_url, payload=bind_to_interface, cookies=cookies)
    return response


def create_epg(base_url, cookies, tenant_name, ap, epg, bd):
    # epg_url_template = Template('node/mo/uni/tn-${tenant_name}/ap-${ap_name}/epg-${epg}.json')
    # epg_url = epg_url_template.substitute(tenant_name=tenant_name, ap_name=ap, epg=epg)
    # new_url = url + epg_url
    epg_url_template_full = '{}node/mo/uni/tn-{}/ap-{}/epg-{}.json'.format(base_url, tenant_name,ap,epg)
    epg_create_template = Template('{"fvAEPg":{"attributes":{"dn":"uni/tn-${tenant_name}/ap-${ap}/epg-${epg}","name":"${epg}","rn":"epg-${epg}","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"${bd_name}","status":"created,modified"},"children":[]}}]}}')
    epg_create = epg_create_template.substitute(tenant_name=tenant_name, ap=ap, epg=epg, bd_name=bd)

    new_epg = make_post_api_call(epg_url_template_full, payload=epg_create, cookies=cookies)
    return epg_url_template_full


def bind_epg_to_physdom(epg_url, cookies, physdom):

    physdom_template=Template('{"fvRsDomAtt":{"attributes":{"resImedcy":"immediate","tDn":"uni/phys-${name}","status":"created"},"children":[]}}')

    physdom = physdom_template.substitute(name=physdom)
    response = make_post_api_call(epg_url, payload=physdom, cookies=cookies)
    return response


def get_vlan_id(vlan_name):
    m = re.search('(?<=-)\w+', vlan_name)
    vlan_id = m.group(0)
    return int(vlan_id)


def vlan_pool_details(base_url, cookies, physdom):
    # vlan_pool_template = Template('node/mo/uni/phys-${physdom}.json?query-target=children&target-subtree-class=infraRsVlanNs')
    # vlan_pool_name = vlan_pool_template.substitute(physdom=physdom)
    # new_url = url + vlan_pool_name

    vlan_pool_name_full_url = '{}node/mo/uni/phys-{}.json?query-target=children&target-subtree-class=infraRsVlanNs'.format(base_url,physdom)
    get_vlan_pool_name = make_get_api_call(vlan_pool_name_full_url, cookies=cookies)

    vlan_pool = get_vlan_pool_name.text

    vlan_pool_json = json.loads(vlan_pool)
    vlan_pool_name = vlan_pool_json['imdata'][0]['infraRsVlanNs']['attributes']['tDn']
    # vlan_pool_details_template = Template('node/mo/${vlan_pool_name}.json?query-target=children&target-subtree-class=fvnsEncapBlk')
    # vlan_pool_details = vlan_pool_details_template.substitute(vlan_pool_name=vlan_pool_name)
    # new_url = url + vlan_pool_details

    vlan_pool_details_full_url = '{}node/mo/{}.json?query-target=children&target-subtree-class=fvnsEncapBlk'.format(base_url,vlan_pool_name)
    get_vlan_pool_details = make_get_api_call(vlan_pool_details_full_url, cookies=cookies)
    vlan_pool_details = get_vlan_pool_details.text
    print(vlan_pool_details)

    vlan_pool_dets = json.loads(vlan_pool_details)
    from_vlan = vlan_pool_dets['imdata'][0]['fvnsEncapBlk']['attributes']['from']
    to_vlan = vlan_pool_dets['imdata'][0]['fvnsEncapBlk']['attributes']['to']

    return from_vlan, to_vlan


def create_epg_port(event, context):
    #TODO context variable passing???
    url = event['sessionAttributes']['url']
    username = event['sessionAttributes']['username']
    password = event['sessionAttributes']['password']
    print('123')
    cookies = aci_login(url, username, password)
    slots = event['currentIntent']['slots']
    tenant_name = event['currentIntent']['slots']['tenant_name'] or 'Heroes'
    ap = event['currentIntent']['slots']['ap_name'] or 'Save_The_Planet'
    epg = event['currentIntent']['slots']['epg_name']
    leaf = event['currentIntent']['slots']['leaf_id']
    port = event['currentIntent']['slots']['port']
    bd = event['currentIntent']['slots']['bd_name']
    physdom = event['currentIntent']['slots']['physdom_name'] or 'Heroes_phys'
    vlan_id = event['currentIntent']['slots']['vlan_id']
    subnet = event['currentIntent']['slots']['subnet']
    print('456')
    tenant_exists = check_tenant_exists(url, cookies, tenant_name)
    ap_exists = check_ap_exists(url, cookies, tenant_name, ap)
    bd_exists = check_bd_exists(url, cookies, tenant_name, bd)
    print(tenant_exists)
    print(ap_exists)
    print(bd_exists)
    if tenant_exists == False:
        create_tenant(url, cookies, tenant_name)
    if ap_exists == False:
        create_ap(url, cookies, tenant_name, ap)
    if bd_exists == False:
        print('BD doesnt exist')
        create_bd_w_subnet(url, cookies, tenant_name, bd, subnet)
    print('789')
    epg_url = create_epg(url, cookies, tenant_name, ap, epg, bd)
    epg_physdom_response = bind_epg_to_physdom(epg_url, cookies, physdom)
    from_vlan, to_vlan = vlan_pool_details(url, cookies, physdom)
    vlan_outside_pool_range = 'vlan_id for physdom {} shall be between {} and {}'.format(physdom, from_vlan, to_vlan)
    from_vlan_id = get_vlan_id(from_vlan)
    to_vlan_id = get_vlan_id(to_vlan)
    print('10,11,12')

    if (int(vlan_id) > to_vlan_id or int(vlan_id) < from_vlan_id):
        return generate_response_code(event,slots,
                                      dialog_type="ELICITSLOT",
                                      slot_to_elicit="vlan_id",
                                      intent=event['currentIntent']['name'],
                                      message=vlan_outside_pool_range)
        # return {
        #     "dialogAction": {
        #         "type": "ElicitSlot",
        #         "intentName": event['currentIntent']['name'],
        #         "slots": slots,
        #         "slotToElicit": "vlan_id",
        #         "message": {"contentType": "PlainText", "content": vlan_outside_pool_range}
        #     }
        # }

    epg_interface_bind = bind_epg_to_interface(epg_url, cookies, vlan_id, leaf, port)
    epg_created = 'epg {} within App {} belonging to Tenant {} has been created & is associated with physdom {} leaf {} and port {}'.format(epg, ap, tenant_name, physdom, leaf, port)
    intent_fulfilled = generate_response_code(event,"SKIP",
                                          dialog_type="CLOSEFULLFILLED",
                                          message=epg_created)
    return intent_fulfilled
    # intent_fulfilled = {
    #     "dialogAction": {
    #         "type": "Close",
    #         "fulfillmentState": "Fulfilled",
    #         "message": {"contentType": "PlainText", "content": epg_created}
    #     }
    # }



if __name__ == "__main__":
    create_epg_port('event', 'context')
