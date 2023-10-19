from netmiko import ConnectHandler
from getpass import getpass


def getConnectionHandler(host, username, passw):
    try:
        device = { 
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": passw,
        "secret": passw
         }
        device_connect =  ConnectHandler(**device) 
        device_connect.enable()
        return device_connect
    except:
        print("Failed to authenticate to host: "+ host)
        exit(1)

