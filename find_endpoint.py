import json
import csv
import re

def find_endpoint(endpoint_ip,url,cookies):
    print(url)
    endpoints_url= url + "node/class/fvCEp.json?query-target-filter=and(eq(fvCEp.ip, "'"{}"'"))".format(endpoint_ip)
    print(endpoints_url)
    output_raw = make_get_api_call(endpoints_url, cookies=cookies)
    make_get_api_call(epg_info, cookies=cookies)
    temp1 = output_raw.text
    print(temp1)
    temp=str(temp1)
    temp_dict=json.loads(temp)
    print(temp_dict)
    endpoint=temp_dict['imdata'][0]
    file_name='/tmp/endpoint.csv'
    dn=endpoint['fvCEp']['attributes']['dn']
    ip=endpoint['fvCEp']['attributes']['ip']
    mac=endpoint['fvCEp']['attributes']['mac']
    encap=endpoint['fvCEp']['attributes']['encap']
    reg='/'
    dn_list=[]
    dn_list=dn.split(reg)
    tenant_name=dn_list[1]
    ap_profile=dn_list[2]
    epg=dn_list[3]
    cep=dn_list[4]
    expression=r'epg-(.*)'
    epg1 = re.search(expression, epg)
    epg_name=epg1.group(1)
    epg_info= url + "node/class/fvAEPg.json?query-target=children"
    epg_output_raw=output_raw =make_get_api_call(epg_info, cookies=cookies)
    temp = epg_output_raw.text
    temp_dict=json.loads(temp)

    epg_list=temp_dict['imdata']
    for a in epg_list:
        print a
    mystring='uni/{}/{}/{}'.format(tenant_name,ap_profile,epg)
    print(mystring)
    cons_list=[]
    prov_list=[]
    #Find the consumed & provided contracts
    for item in epg_list:
     try:
       if mystring in item['fvRsProv']['attributes']['dn']:
           prov_list.append(item)
     except:
       continue
    for item in epg_list:
     try:
       if mystring in item['fvRsCons']['attributes']['dn']:
           cons_list.append(item)
     except:
       continue

    if cons_list:
        consumed_contract=cons_list[0]['fvRsCons']['attributes']['tnVzBrCPName']
    else:
        consumed_contract=''

    if prov_list:
        provided_contract=prov_list[0]['fvRsProv']['attributes']['tnVzBrCPName']
    else:
        provided_contract=''


    with open(file_name,'w') as f:
        row1="ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract \n"
        data=(("{},{},{},{},{},{},{},\n").format(ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract))
        f.write(row1),f.write(data)

    return file_name
