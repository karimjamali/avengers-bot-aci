import json

def lambda_handler(event, context):

    message='*Hello from the Avengers ACI Bot* \n\n'
    message+='I can help in *provisioning & troubleshooting your ACI Fabric*.'
    message+='Rest Assured that my capabilities will expand with time \n\n'
    message+='Kindly use these *utterances* when talking to me: \n'
    message+='*login* will initiate the login process \n'
    message+='*help* will replay the utterances for proper interaction \n'
    message+='*new tenant* will help you create a new tenant \n'
    message+='*new app* will help you create a new application profile within a tenant\n'
    message+='*new bd* will help you create a new bridge domain\n'
    message+='*new epg* will help you create a new endpoint group within an Application Profile\n'
    message+='*bind epg to an interface* will create \n'
    message+='*snapshot* will take a local backup of the configuration on the APIC\n\n'
    message+='*Please start by typing login to initiate the login process* \n'

    cookies_resp = {
        "dialogAction": {
            "type": "ElicitIntent",
            "message": {"contentType": "PlainText","content": message }
            }
    }
    return cookies_resp
