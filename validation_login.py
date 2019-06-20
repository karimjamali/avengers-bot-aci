from fqdn import FQDN
from messages import apic_fqdn_retry
from utils import generate_response_code

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
        fqdn = FQDN(str(domain))
        if not fqdn.is_valid:
            print('FQDN is not valid')

            return generate_response_code(event,slots,
                                          dialog_type="ELICITSLOT",
                                          intent=event['currentIntent']['name'],
                                          slot_to_elicit="fqdn",
                                          message=apic_fqdn_retry)

        else:
           return generate_response_code(event,slots,dialog_type="DELEGATE")

    else:
        return generate_response_code(event,slots,dialog_type="DELEGATE")
