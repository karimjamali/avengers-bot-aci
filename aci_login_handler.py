from messages import logged_in_message
from utils import aci_login, generate_response_code


def fix_url(url):
    # the objective is to solve the challenge with the slack output to return a proper fqdn
    reg = '|'
    list = []
    list = url.split(reg)
    if len(list) == 1:
        return url
    else:
        url = 'https://' + list[1]
        return url


def login_handler(event, context):
    # Login to APIC & return message to user, pass username,password & url attributes in the ElicitIntent for further processing
    print(event)
    url_tmp = event['currentIntent']['slots']['fqdn']
    username = event['currentIntent']['slots']['username']
    password = event['currentIntent']['slots']['password']
    url = 'https://' + url_tmp + '/api/'
    url = fix_url(url)

    cookies = aci_login(url, username, password)
    if type(cookies) is str:
        mymessage = cookies
    else:
        mymessage = logged_in_message
        sessionAttributes = {"url": url, "username": username, "password": password}

    cookies_resp = generate_response_code(event,"SKIP",
                                          dialog_type="ELICIT",
                                          message=mymessage,
                                          sessionattributes=sessionAttributes)
        # cookies_resp = {
        #     "sessionAttributes": sessionAttributes,
        #     "dialogAction": {
        #         "type": "ElicitIntent",
        #         "message": {"contentType": "PlainText", "content": mymessage}
        #     }
        #
        # }

    print(cookies_resp)
    return cookies_resp


if __name__ == "__main__":
    login_handler('event', 'context')
