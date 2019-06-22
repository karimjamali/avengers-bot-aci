from fqdn import FQDN
from messages import apic_fqdn_retry
from utils import generate_response_code
import ipaddress

def is_ip_or_domain(my_input):
    is_ip = False
    is_domain = False
    try:
        ipaddress.ip_address(my_input)
        is_ip = True
    except ValueError:
        if FQDN(my_input).is_valid:
            is_domain = True
    except Exception:
        print("something else")

    if is_domain or is_ip:
        return True

def fix_url(url):
    # the objective is to solve the challenge with the slack output to return a proper fqdn
    reg = '|'
    list = []
    list = url.split(reg)
    if len(list) == 1:
        return url
    else:
        url = list[1]
        return url


def validate(event,context):
    print(event)
    domain=event['currentIntent']['slots']['fqdn']
    slots=event['currentIntent']['slots']
    print(domain)
    if domain is not None:
        domain=fix_url(domain)
        if not is_ip_or_domain(domain):
            print('Domain is not valid')
            return generate_response_code(event,slots,
                                          dialog_type="ELICITSLOT",
                                          intent=event['currentIntent']['name'],
                                          slot_to_elicit="fqdn",
                                          message=apic_fqdn_retry)

        else:
           print('Domain is valid')
           return generate_response_code(event,slots,dialog_type="DELEGATE")

    else:
        return generate_response_code(event,slots,dialog_type="DELEGATE")
