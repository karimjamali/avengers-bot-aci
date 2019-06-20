import json

def lambda_handler(event, context):

    message = '\n*Hello from the Avengers ACI Bot!*\n\nI can help you in provisioning your ACI fabric. Here are the commands that I support:\n\n-   *“help”*- You can always review these commands simply by typing help.\n\n-   *“tenants”*- This will start a dialog to create Tenants.\n\n-   *“App profile”*- This will start a dialog create Application Network Profile.\n\n-   *“Bridge Domain”*- This will start a dialog create Bridge Domain.\n\n-   *“add subnet”*- This will start a dialog to add additional subnets to an existing Bridge Domain.\n\n-   *“EPG”*- This will start a dialog to create EPG and Associate to Physical or Virtual Domain.\n\n-   *“Troubleshooting”*- This will start a dialog to troubleshoot communication between source and Destination IP address.\n\n-   *“Snapshot”*- This will start a dialog to take a snapshot of the fabric.\n'
    cookies_resp = {
        "dialogAction": {
            "type": "ElicitIntent",
            "message": {"contentType": "PlainText","content": message }
            }
    }
    return cookies_resp
