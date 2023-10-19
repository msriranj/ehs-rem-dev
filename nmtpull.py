import traceback
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getNetworkDeviceData (url, filter_template):
    try:

        _headers = {'Authorization': 'basic 229c1728-c73e-4478-bdec-23471d2bf546', 'Content-Type': 'application/json', 'Accept': "application/json"}
        resp = requests.post(url=url, data=json.dumps(filter_template), headers=_headers, verify=False)
        if resp.status_code == 200:
            data = resp.json()['NWDevicesData']
            return (data)

    except Exception:
        print ("error :", traceback.format_exc())
       

def generateKeyValuePairs (devices):
    device_dict = dict((x['DeviceName'], x) for x in devices)
    return device_dict

def pullDevices(site_code):
    
    _url = 'https://networkmanageability.app.intel.com/api/NWDevices/GetNWDevicedata'
    _filter_template_ccr1 = {
            "exclusionParameter": {
                "building": [],
                "campus": [],
                "country": [],
                "device": [],
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "wildcard": ['odc']
            },
            "inclusionParameter": {
                "building": [],
                "campus": [site_code],
                "country": [],
                "device": [],
                "entireNetwork": "false",
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "domain": ["office"],
                "wildcard": ['CCR1.','ccr1.','CCR01.','ccr01.','CCS1.','ccs1.','CCS01.','ccs01.']
            }
    }
    _filter_template_ccr2 = {
            "exclusionParameter": {
                "building": [],
                "campus": [],
                "country": [],
                "device": [],
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "wildcard": ['odc']
            },
            "inclusionParameter": {
                "building": [],
                "campus": [site_code],
                "country": [],
                "device": [],
                "entireNetwork": "false",
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "domain": ["office"],
                "wildcard": ['CCR2.','ccr2.','CCR02.','ccr02.','CCS2.','ccs2.','CCS02.','ccs02.']
            }
    }
    _filter_template_obr1 = {
            "exclusionParameter": {
                "building": [],
                "campus": [],
                "country": [],
                "device": [],
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "wildcard": ['odc']
            },
            "inclusionParameter": {
                "building": [],
                "campus": [site_code],
                "country": [],
                "device": [],
                "entireNetwork": "false",
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "domain": ["office"],
                "wildcard": ['OBR1.','obr1.','OBR01.','obr01.']
            }
    }
    _filter_template_obr2 = {
            "exclusionParameter": {
                "building": [],
                "campus": [],
                "country": [],
                "device": [],
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "wildcard": ['odc']
            },
            "inclusionParameter": {
                "building": [],
                "campus": [site_code],
                "country": [],
                "device": [],
                "entireNetwork": "false",
                "model": [],
                "osVersion": [],
                "region": [],
                "site": [],
                "vendor": [],
                "domain": ["office"],
                "wildcard": ['OBR2.','obr2.','OBR02.','obr02.']
            }
    }


    ccr1_query = getNetworkDeviceData(_url, _filter_template_ccr1)
    ccr1_dict = generateKeyValuePairs (ccr1_query)
    ccr1 = list(ccr1_dict.keys())

    ccr2_query = getNetworkDeviceData(_url, _filter_template_ccr2)
    ccr2_dict = generateKeyValuePairs (ccr2_query)
    ccr2 = list(ccr2_dict.keys())

    obr1_query = getNetworkDeviceData(_url, _filter_template_obr1)
    obr1_dict = generateKeyValuePairs (obr1_query)
    obr1 = list(obr1_dict.keys())

    obr2_query = getNetworkDeviceData(_url, _filter_template_obr2)
    obr2_dict = generateKeyValuePairs (obr2_query)
    obr2 = list(obr2_dict.keys())

    try:
        if (len(ccr1) == 1 and len(ccr2) == 1 and len(obr1) == 1 and len(obr2) == 1):
            return [ccr1[0],ccr2[0],obr1[0],obr2[0]]
        else:
            
            print("Failed to get CCRs and OBRs ......... E X I T I N G........")
            exit(1)
            return []

    except:
        print("Failed to get CCRs and OBRs ......... E X I T I N G........")
        exit(1)
        
    
# print(nmtpull('hF'))
