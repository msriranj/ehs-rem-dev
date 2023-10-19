import nmtpull
import connhandlers as connect
from netmiko import ConnectHandler
from getpass import getpass
from tabulate import tabulate
from jinja2 import Environment, FileSystemLoader

def failed(msg):
    print(f" SCRIPT TERMINATED: {msg}")
    exit(1)

def getDevices(site_code):
    return nmtpull.pullDevices(site_code)

def getPorts(ccr1_connect,ccr2_connect,obr1,obr2,obr1_connect):

    ccr1_obr1_line = ccr1_connect.send_command(f'show cdp entry {obr1} | i Interface')
    ccr1_obr2_line = ccr1_connect.send_command(f'show cdp entry {obr2} | i Interface')

    ccr2_obr1_line = ccr2_connect.send_command(f'show cdp entry {obr1} | i Interface')
    ccr2_obr2_line = ccr2_connect.send_command(f'show cdp entry {obr2} | i Interface')

    obr1_obr2_line = obr1_connect.send_command(f'show cdp entry {obr2} | i Interface')

    if ccr1_obr1_line == '' or ccr1_obr2_line == '' or ccr2_obr1_line == '' or ccr2_obr2_line == '': failed('Failed to retrieve ports  ........ E X I T I N G ......')
       
    else:
        
        try:
            
            ccr1_obr1 = str(ccr1_obr1_line.split(',')[0].split(':')[1]).strip()
            ccr1_obr2 = str(ccr1_obr2_line.split(',')[0].split(':')[1]).strip()
            ccr2_obr1 = str(ccr2_obr1_line.split(',')[0].split(':')[1]).strip()
            ccr2_obr2 = str(ccr2_obr2_line.split(',')[0].split(':')[1]).strip()

            obr1_ccr1 = str(ccr1_obr1_line.split(',')[1].split(':')[1]).strip()
            obr1_ccr2 = str(ccr2_obr1_line.split(',')[1].split(':')[1]).strip()
            obr2_ccr1 = str(ccr1_obr2_line.split(',')[1].split(':')[1]).strip()
            obr2_ccr2 = str(ccr2_obr2_line.split(',')[1].split(':')[1]).strip()

            obr1_obr2 = str(obr1_obr2_line.split(',')[0].split(':')[1]).strip()

            return [ccr1_obr1,ccr1_obr2,ccr2_obr1,ccr2_obr2,obr1_ccr1,obr1_ccr2,obr2_ccr1,obr2_ccr2,obr1_obr2]

        except:
            failed('Failed to retrieve ports  ........ E X I T I N G ......')

def getASN(ccr1_connect,ccr2_connect,obr1_connect,obr2_connect):
    try:
        ccr1_asn = str(ccr1_connect.send_command('show run | i ^router bgp').split('bgp')[1]).strip()
        ccr2_asn = str(ccr2_connect.send_command('show run | i ^router bgp').split('bgp')[1]).strip()
        obr1_asn = str(obr1_connect.send_command('show run | i ^router bgp').split('bgp')[1]).strip()
        obr2_asn = str(obr2_connect.send_command('show run | i ^router bgp').split('bgp')[1]).strip()

        return [ccr1_asn,ccr2_asn,obr1_asn,obr2_asn]
    except:
        failed(" Could not retrieve BGP ASN numbers of devices ")

def preValidations(ccr1_connect,ccr2_connect,obr1_connect,obr2_connect,obr1_obr2):

    ccr1_vrf_check = ccr1_connect.send_command('show ip vrf | i ehs')
    ccr2_vrf_check = ccr2_connect.send_command('show ip vrf | i ehs')

    
    obr1_vrf_check = obr1_connect.send_command('show ip vrf | i ehs')
    obr2_vrf_check = obr1_connect.send_command('show ip vrf | i ehs')

    if (obr1_vrf_check == '' or obr2_vrf_check == ''):
      failed("EHS vrf not found on obR ")
     
    else:
       print(" EHS vrf pre-configured check ----> Pass")



    if (ccr1_vrf_check == '' or ccr2_vrf_check == ''):
      failed("EHS vrf not found on CCR ")
     
    else:
       print(" EHS vrf pre-configured check ----> Pass")


    obr1_vlan_check = obr1_connect.send_command('show ip int bri | i Vlan4021|Vlan4023|Vlan4024')
    obr1_l2_vlan_check = obr1_connect.send_command('show vlan | i ^4021|^4023|^4024')

    obr2_vlan_check = obr2_connect.send_command('show ip int bri | i Vlan4021|Vlan4025|Vlan4026')
    obr2_l2_vlan_check = obr1_connect.send_command('show vlan | i ^4021|^4025|^4026')

    ccr1_vlan_check = ccr1_connect.send_command('show ip int bri | i Vlan4023|Vlan4025')
    ccr1_l2_vlan_check = obr1_connect.send_command('show vlan | i ^4023|^4024')

    ccr2_vlan_check = ccr2_connect.send_command('show ip int bri | i Vlan4024|Vlan4026')
    ccr2_l2_vlan_check = obr1_connect.send_command('show vlan | i ^4023|^4026')

    ## sh vlan to be added

    if (obr1_vlan_check == obr2_vlan_check == ccr1_vlan_check == ccr2_vlan_check == ''):
        print(" Vlans available ----> Pass")
    else:
        failed(" Vlans validation failed : Vlans already exist on device")

    if (obr1_l2_vlan_check == obr2_l2_vlan_check == ccr1_l2_vlan_check == ccr2_l2_vlan_check == ''):
        print(" L2 Vlans available ----> Pass")
    else:
        failed(" Vlans validation failed : L2 Vlans already exist on device")

    obr1_scope_check = obr1_connect.send_command('show ip route vrf ehs | i 10.250.128.')
    obr2_scope_check = obr2_connect.send_command('show ip route vrf ehs | i 10.250.128.')
    ccr1_scope_check = ccr1_connect.send_command('show ip route vrf ehs | i 10.250.128.')
    ccr2_scope_check = ccr2_connect.send_command('show ip route vrf ehs | i 10.250.128.')

    if (obr1_scope_check == obr2_scope_check == ccr1_scope_check == ccr2_scope_check == ''):
         print(" Scopes not pre-configured ----> Pass")
    else:
         failed(" IP Scopes validation failed : IP scopes already exist on device")

    obr1_pc_check = obr1_connect.send_command(f'sh run interface {obr1_obr2}| i channel-group 1')
    obr2_pc_check = obr2_connect.send_command(f'sh run interface {obr1_obr2}| i channel-group 1')

    # | find obr ports find channel grp 

    if (obr1_pc_check == '' or obr2_pc_check == ''):
      failed("Port-Channel 1 not configured ")
     
    else:
       print(" Port-Channel Validation ----> Pass")

    
    return True

def getTemplates(ccr1_obr1,ccr1_obr2,ccr2_obr1,ccr2_obr2,obr1_ccr1,obr1_ccr2,obr2_ccr1,obr2_ccr2,ccr1_asn,ccr2_asn,obr1_asn,obr2_asn,ccr1_prefix_flag,ccr2_prefix_flag,ccr1_route_map_flag,ccr2_route_map_flag):
    template_dir = 'C:\\Users\\msriranj\\OneDrive - Intel Corporation\\Desktop\\My Python Workspace\\Office\\Remidiation_network_landing\\templates'
    env = Environment(loader=FileSystemLoader(template_dir))
    print("Template function: OBR2->ccr2: ",obr2_ccr1,obr2_ccr2)
    template_vars = {
        'obr1': {
            'obr1_ccr1': obr1_ccr1,
            'obr1_ccr2': obr1_ccr2,
            'obr1_asn': obr1_asn,
            'obr2_asn': obr2_asn,
            'ccr1_asn': ccr1_asn,
            'ccr2_asn': ccr2_asn
        },
         'obr2': {
            'obr2_ccr1': obr2_ccr1,
            'obr2_ccr2': obr2_ccr2,
            'obr1_asn': obr1_asn,
            'obr2_asn': obr2_asn,
            'ccr1_asn': ccr1_asn,
            'ccr2_asn': ccr2_asn
        },
        'ccr1':{
            'ccr1_obr1': ccr1_obr1,
            'ccr1_obr2': ccr1_obr2,
            'obr1_asn': obr1_asn,
            'obr2_asn': obr2_asn,
            'ccr1_asn': ccr1_asn,
            'prefix_flag': ccr1_prefix_flag,
            'route_map_flag': ccr1_route_map_flag

        },
         'ccr2':{
            'ccr2_obr1': ccr2_obr1,
            'ccr2_obr2': ccr2_obr2,
            'obr1_asn': obr1_asn,
            'obr2_asn': obr2_asn,
            'ccr2_asn': ccr2_asn,
            'prefix_flag': ccr2_prefix_flag,
            'route_map_flag': ccr2_route_map_flag

        },
        
}
    obr1_template = env.get_template('obr1.j2')
    obr1_commands = obr1_template.render(template_vars['obr1']).splitlines()

    obr2_template = env.get_template('obr2.j2')
    obr2_commands = obr2_template.render(template_vars['obr2']).splitlines()

    ccr1_template = env.get_template('ccr1.j2')
    ccr1_commands = ccr1_template.render(template_vars['ccr1']).splitlines()

    ccr2_template = env.get_template('ccr2.j2')
    ccr2_commands = ccr2_template.render(template_vars['ccr2']).splitlines()

    return[obr1_commands,obr2_commands,ccr1_commands,ccr2_commands]

    

    
def main():

    line = '********************'

   ###################### USER Inputs ###########################

    site_code = input('Please enter a valid site code: ')
    username = input("Enter username: ")
    passw = getpass("Enter password: ")
   
   ######################### Initialize devices ##################
   
    print(f'{line} R E T R I V I N G   D E V I C E S {line}')
    
    devices = getDevices(site_code)
    ccr1, ccr2, obr1, obr2 = devices

    print(" CCRS: ",ccr1,ccr2)
    print(" OBRS: ",obr1,obr2)

    ############### Establish connection handlers #################

    print(f'{line} ESTABLISHING CONNECTION {line}')

    ccr1_connect = connect.getConnectionHandler(ccr1,username,passw)
    ccr2_connect = connect.getConnectionHandler(ccr2,username,passw)
    obr1_connect = connect.getConnectionHandler(obr1,username,passw)
    obr2_connect = connect.getConnectionHandler(obr1,username,passw)

    print('Connections Successfull!')

    ##################### get ports ###########################
    
    print(f'{line} GETTING PORT DETAILS {line}')

    ccr1_obr1,ccr1_obr2,ccr2_obr1,ccr2_obr2,obr1_ccr1,obr1_ccr2,obr2_ccr1,obr2_ccr2,obr1_obr2 = getPorts(ccr1_connect,ccr2_connect,obr1,obr2,obr1_connect)
    
    print('Local and remote ports retrieved')

    print(ccr1_obr1,ccr1_obr2,ccr2_obr1,ccr2_obr2,obr1_ccr1,obr1_ccr2,obr2_ccr1,obr2_ccr2)

    ################### pre-change validations ##############################

    print(f'{line} P R E - C H A N G E   V A L I D A T I O N S {line}')

    if preValidations(ccr1_connect,ccr2_connect,obr1_connect,obr2_connect,obr1_obr2):
        print("Validations success!")

    ###################### get asn numbers and validate#########################

    print(f'{line} GETTING ASN {line}')
    
    ccr1_asn,ccr2_asn,obr1_asn,obr2_asn = getASN(ccr1_connect,ccr2_connect,obr1_connect,obr2_connect)
    print(ccr1_asn,ccr2_asn,obr1_asn,obr2_asn)

    ###################### build templates for OBRs #################################

    if ccr1_connect.send_command('sh ip prefix-list  | i DENY-DEFAULT-ROUTE') == '' : ccr1_prefix_flag = True
    else: ccr1_prefix_flag = False
    if ccr2_connect.send_command('sh ip prefix-list  | i DENY-DEFAULT-ROUTE') == '' : ccr2_prefix_flag = True
    else: ccr2_prefix_flag = False

    if ccr1_connect.send_command('sh route-map | i route-map DENY-DEFAULT') == '' : ccr1_route_map_flag = True
    else: ccr1_route_map_flag = False
    if ccr2_connect.send_command('sh route-map | i route-map DENY-DEFAULT') == '' : ccr2_route_map_flag = True
    else: ccr2_route_map_flag = False

    obr1_config, obr2_config, ccr1_config, ccr2_config = getTemplates(ccr1_obr1,ccr1_obr2,ccr2_obr1,ccr2_obr2,obr1_ccr1,obr1_ccr2,obr2_ccr1,obr2_ccr2,ccr1_asn,ccr2_asn,obr1_asn,obr2_asn,ccr1_prefix_flag,ccr2_prefix_flag,ccr1_route_map_flag,ccr2_route_map_flag)

    print("Config genereated....")
    print(f'{line} P U S H I N G    C O N F I G S {line}')

    print(":::OBR1:::\n")
    for x in obr1_config: print(x)
    print(":::OBR2:::\n")
    for x in obr2_config: print(x)
    print(":::CCR1:::\n")
    for x in ccr1_config: print(x)
    print(":::CCR2:::\n")
    for x in ccr2_config: print(x)

    ############send_config_set_command
   

    print(f'{line} C O N F I G S  P U S H E D !!!! {line}')

    ccr1_connect.disconnect()
    ccr2_connect.disconnect()
    obr1_connect.disconnect()
    obr2_connect.disconnect()

if __name__ == '__main__':
    main()


