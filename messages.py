#login messages
logged_in_message = "*Congratulations , you have logged in successfully* , please type *help* to figure out the possible options"
login_challenge='*Oops, I still can\'t login successfully to the APIC, please check the url and credentials* '

#login vaildation
apic_fqdn_retry= "*APIC FQDN is not correct , please make sure you enter a Fully Qualified Domain Name* "


#snapshot
snapshot_created_template='*snapshot has been created & stored locally with description {}* '
snapshot_failed='*There was an error creating the snapshot* '

#Tenant
tenant_created_message='*Tenant {} has been created successfully* !'
tenant_failed_message='*There was a problem creating Tenant {}* '
tenant_exists_message='*Tenant {} is already available on APIC, thus we did not create it* '


#Application Profile
tenant_ap_exist_message='*Tenant {}  and Application Profile {} both exist!* '
tenant_exists_ap_created_message='*Tenant {} exists, and we just created Application Profile {}* '
error_create_app_profile_message='*Unfortunately, we could not create Application Profile {} under tenant {}*  '
tenant_not_exist_message='*Tenant {} doesn\'t exist, please type create tenant and then try to create application profile* '


#BD
tenant_bd_exist_message='*Tenant {}  and Bridge Domain {} both exist!* '
tenant_exists_bd_created_message='*Tenant {} exists, and we just created Bridge Domain {}* '

#EPG
ap_epg_exist_message='*Application Profile {} and EPG {} both exist* '
ap_exists_epg_created_message='*AP {} exists, and we just created EPG {}* '
ap_not_exist_message='*Under Tenant {}, Application Profile {} doesn\'t exist, please create one* '



#Utils ACI Login
url_error = '*Please Check the URI as we have a 404 Error* '
url_credentials_error = '*Please Check the credentials as we have a 401 Error* '

#common
not_logged_in='*You have not logged in, please type login to proceed* '

#EPG
bd_specify_subnet='*Please specify the gateway address/mask for BD {}* '
ap_exists_epg_bd_created_message='*AP {} exists, and we just created EPG {} with BD {} and subnet {}* '
epg_create_error_message='*Oops, something went wrong and we couldnot create EPG* '
ap_bd_exists_epg_created_message='*AP {} & BD {} exist, and we just created EPG {}* '


#bind epg to interface
epg_not_exist_message='*EPG {} doesnt exist, please create it first by the utterance new epg* '
vlan_outside_pool_range_message='*vlan id for physdom {} shall be between {} and {}, please choose another value* '
epg_bind_to_interface_message='*EPG {} within Application Profile {} belonging to Tenant {} has been created & is associated with physdom {} leaf {} and port {}* '
