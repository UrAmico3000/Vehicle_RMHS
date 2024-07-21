from readOBDValues import api_url
import requests
import json


def send_PID_values(PID):
    _data = PID
    _data["username"] = "tirth"
    print(f'http://{api_url}/sensor/set and data is {_data}')
    json_object = json.dumps(_data, indent=4)
    response = requests.post(f'http://{api_url}/sensor/set', data=json_object,
                             headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f'Failed to send PID return status code is {response.status_code}')


def send_DTC_values(DTC):
    _data = DTC
    _data["username"] = "tirth"
    print(f'http://{api_url}/dtc/set and data is {_data}')
    dtc_list = json.dumps(_data, indent=4)
    response = requests.post(f'http://{api_url}/dtc/set', data=dtc_list, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f'Failed to send DTC return status code is {response.status_code}')
