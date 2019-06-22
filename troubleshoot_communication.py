import boto3
import os
import csv
import re
import json
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from utils import aci_login, generate_response_code,make_get_api_call,validate_if_logged_in
from source_email import from_email


def find_endpoint(endpoint_ip,url,cookies):
    endpoints_url= url + "node/class/fvCEp.json?query-target-filter=and(eq(fvCEp.ip, "'"{}"'"))".format(endpoint_ip)
    output_raw = make_get_api_call(endpoints_url, cookies=cookies)
    print(endpoints_url)
    temp1 = str(output_raw.text)
    temp3=json.loads(temp1)
    file_name='/tmp/endpoint.csv'
    print(temp3)
    endpoint=temp3['imdata'][0]
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
    epg_output_raw=output_raw = make_get_api_call(epg_info, cookies=cookies)
    temp = epg_output_raw.text
    temp_dict=json.loads(temp)
    epg_list=temp_dict['imdata']
    mystring='uni/{}/{}/{}'.format(tenant_name,ap_profile,epg)
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

    return ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract


def temporary_email(dest_email):
    reg = '|'
    if reg in dest_email:
        list = []
        list = dest_email.split(reg)
        to_email = list[1]
        return to_email
    else:
        return to_email

def send_email_w_attachment(from_email,to_email,subject,filename):
    client = boto3.client(
          'ses',
          region_name='us-east-1',
      )
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email
    part = MIMEText('email body string', 'html')
    message.attach(part)
    part = MIMEApplication(open(filename, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(part)

    response = client.send_raw_email(
          Source=message['From'],
          Destinations=[to_email],
          RawMessage={
              'Data': message.as_string()
          }
      )

def get_endpoints_handler(event, context):
    print(event)
    #Get the url,username,and password from session attributes & tenant_name from slots input, login to APIC, check tenant ap_exists
    #create new tenant if required
    if not validate_if_logged_in(event):
        return generate_response_code(event,"SKIP",dialog_type="ELICIT",
                                      message="You have not logged in, please type login to proceed")

    print(event)
    url=event['sessionAttributes']['url']
    username=event['sessionAttributes']['username']
    password=event['sessionAttributes']['password']
    print(url)
    cookies=aci_login(url,username,password)

    source=event['currentIntent']['slots']['source_ip']
    destination=event['currentIntent']['slots']['destination_ip']
    dest_email=event['currentIntent']['slots']['dest_email']
    subject='*Troubleshooting Session*\n'
    file_name='/tmp/troubleshoot-communications.csv'
    message='*Troubleshooting Session* \n'
    print(source)
    with open(file_name,'w') as f:
      row1="ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract \n"
      try:
        ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract=find_endpoint(source,url,cookies)
        data1=(("{},{},{},{},{},{},{},\n").format(ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract))
        message+='*Source Endpoint Details* \n'
        message+='*IP Address:* {}\n'.format(ip)
        message+='*MAC Address:* {}\n'.format(mac)
        message+='*Tenant:* {}\n'.format(tenant_name)
        message+='*Application Profile:* {}\n'.format(ap_profile)
        message+='*Endpoint Group:* {}\n'.format(epg_name)
        message+='*Consumed Contract:* {}\n'.format(consumed_contract)
        message+='*Provided Contract:* {}\n\n\n'.format(provided_contract)
        print(message)
      except:
        data1='{} does not exist\n'.format(source)
        message+='{} does not exist\n'.format(source)
      try:
        ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract=find_endpoint(destination,url,cookies)
        data2=(("{},{},{},{},{},{},{},\n").format(ip,mac,tenant_name,ap_profile,epg_name,consumed_contract,provided_contract))
        message+='*Destination Endpoint Details* \n'
        message+='*IP Address:* {}\n'.format(ip)
        message+='*MAC Address:* {}\n'.format(mac)
        message+='*Tenant:* {}\n'.format(tenant_name)
        message+='*Application Profile* : {}\n'.format(ap_profile)
        message+='*Endpoint Group:* {}\n'.format(epg_name)
        message+='*Consumed Contract:* {}\n'.format(consumed_contract)
        message+='*Provided Contract:* {}\n\n\n'.format(provided_contract)
        print(message)
      except:
        data2='{} does not exist\n'.format(destination)
        message+='{} does not exist\n'.format(source)
      f.write(row1),f.write(data1),f.write(data2)
    dest_email=temporary_email(dest_email)
    send_email_w_attachment(from_email,dest_email,subject, file_name)
    message+='\n\nWe have gathered all the information about *{}* and *{}* and have sent an email to you about this'.format(source,destination)
    endpoints_resp=generate_response_code(event,"SKIP",dialog_type="CLOSEFULLFILLED",message=message)


    return endpoints_resp


if __name__=="__main__":
   get_endpoints_handler('event','context')
