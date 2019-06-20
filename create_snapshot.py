from string import Template
from messages import snapshot_created_template, snapshot_failed
from utils import make_post_api_call, generate_response_code, aci_login


def create_snapshot(base_url, cookies, description):
    snapshot_url = '{}node/mo/uni/fabric/configexp-defaultOneTime.json'.format(base_url)
    snapshot_payload_template = Template(
        '{\"configExportP\":{\"attributes\":{\"dn\":\"uni/fabric/configexp-defaultOneTime\",\"name\":\"defaultOneTime\",\"snapshot\":\"true\",\"targetDn\":\"\",\"adminSt\":\"triggered\",\"rn\":\"configexp-defaultOneTime\",\"status\":\"created,modified\",\"descr\":\"${descr}\"},\"children\":[]}}')
    snapshot_payload = snapshot_payload_template.substitute(descr=description)

    create_snapshot = make_post_api_call(snapshot_url, payload=snapshot_payload, cookies=cookies)
    return create_snapshot


def snapshot_handler(event, context):
    # Get the url,username,and password from session attributes
    print(event)

    url = event['sessionAttributes']['url']
    username = event['sessionAttributes']['username']
    password = event['sessionAttributes']['password']

    cookies = aci_login(url, username, password)

    slots = event['currentIntent']['slots']
    description = event['currentIntent']['slots']['description']

    response = create_snapshot(url, cookies, description)

    if response.status_code == 200:
        snapshot_created = snapshot_created_template.format(description)
        intent_fulfilled = generate_response_code(event, "SKIP",
                                                  dialog_type="CLOSEFULLFILLED",
                                                  message=snapshot_created
                                                  )

        # intent_fulfilled = {
        #     "dialogAction": {
        #     "type": "Close",
        #     "fulfillmentState": "Fulfilled",
        #     "message": {"contentType": "PlainText","content": snapshot_created }
        #     }
        #     }
        return intent_fulfilled

    else:
        intent_failed = generate_response_code(event, "SKIP",
                                               dialog_type="CLOSEFAILED",
                                               message=snapshot_failed
                                               )
        # intent_failed = {
        #     "dialogAction": {
        #     "type": "Close",
        #     "fulfillmentState": "Failed",
        #     "message": {"contentType": "PlainText","content": snapshot_failed }
        #     }
        #     }
        return intent_failed


if __name__ == "__main__":
    snapshot_handler('event', 'context')
