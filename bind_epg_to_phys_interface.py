import json
import re
from string import Template
from utils import make_get_api_call, make_post_api_call, generate_response_code, get_logindata_from_ddb, aci_login,validate_if_logged_in
from messages import *



def check_epg_exists(base_url, cookies, tenant_name, ap,epg):


    epg_create_url_full = '{}node/mo/uni/tn-{}/ap-{}/epg-{}.json'.format(base_url,tenant_name,ap,epg)
    print(epg_create_url_full)
    epg_exists = make_get_api_call(epg_create_url_full, cookies=cookies)

    json_data = json.loads(epg_exists.text)
    if json_data['imdata'] == []:
        return False
    else:
        return True


def bind_epg_to_interface(epg_url, cookies, vlan_id, leaf, port):

    bind_to_interface_template = Template('{"fvRsPathAtt":{"attributes":{"encap":"vlan-${vlan_id}","instrImedcy":"immediate","tDn":"topology/pod-1/paths-${leaf}/pathep-[${port}]","status":"created"},"children":[]}})')
    bind_to_interface=bind_to_interface_template.substitute(vlan_id=vlan_id,leaf=leaf,port=port)

    response = make_post_api_call(epg_url, payload=bind_to_interface, cookies=cookies)
    return response


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
    if not validate_if_logged_in(event):
        return generate_response_code(event,"SKIP",dialog_type="ELICIT", message=not_logged_in)

    url = event['sessionAttributes']['url']
    username = event['sessionAttributes']['username']
    password = event['sessionAttributes']['password']

    cookies = aci_login(url, username, password)

    slots = event['currentIntent']['slots']

    tenant_name = event['currentIntent']['slots']['tenant_name'] or 'Heroes'
    ap = event['currentIntent']['slots']['ap_name'] or 'Save_The_Planet'
    epg = event['currentIntent']['slots']['epg_name']
    leaf = event['currentIntent']['slots']['leaf_id']
    port = event['currentIntent']['slots']['port']
    physdom = event['currentIntent']['slots']['physdom_name'] or 'Heroes_phys'
    vlan_id = event['currentIntent']['slots']['vlan_id']


    epg_url = '{}node/mo/uni/tn-{}/ap-{}/epg-{}.json'.format(url, tenant_name,ap,epg)

    print(epg_url)

    if not check_epg_exists(url, cookies, tenant_name, ap,epg):
        epg_not_exist_msg=epg_not_exist_message.format(epg)
        return generate_response_code(event,"SKIP",dialog_type="ELICIT", message= epg_not_exist_msg)
    else:
        epg_physdom_response = bind_epg_to_physdom(epg_url, cookies, physdom)
        from_vlan, to_vlan = vlan_pool_details(url, cookies, physdom)
        vlan_outside_pool_range_msg = vlan_outside_pool_range_message.format(physdom, from_vlan, to_vlan)
        from_vlan_id = get_vlan_id(from_vlan)
        to_vlan_id = get_vlan_id(to_vlan)
        print(to_vlan_id)
        print(from_vlan_id)
        if (int(vlan_id) > to_vlan_id or int(vlan_id) < from_vlan_id):
            vlan_outside_pool_range_msg=vlan_outside_pool_range_message.format(physdom,from_vlan_id,to_vlan_id)
            return generate_response_code(event,slots,
                                      dialog_type="ELICITSLOT",
                                      slot_to_elicit="vlan_id",
                                      intent=event['currentIntent']['name'],
                                      message=vlan_outside_pool_range_msg)

        epg_interface_bind = bind_epg_to_interface(epg_url, cookies, vlan_id, leaf, port)
        epg_bind_to_interface_msg=epg_bind_to_interface_message.format(epg,ap,tenant_name,physdom,leaf,port)
        intent_fulfilled = generate_response_code(event,"SKIP", dialog_type="CLOSEFULLFILLED",message=epg_bind_to_interface_msg)
        return intent_fulfilled



if __name__ == "__main__":
    create_epg_port('event', 'context')
