import requests
import json

# Load the configuration file
with open('../config.json', 'r') as config_file:
    config = json.load(config_file)

    # Access the API_URL
    api_url = config['API_URL']

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

def sendVIN(VIN):
    _data = {}
    _data["username"] = "tirth"
    _data = json.dumps(_data, indent=4)
    response = requests.put(f'http://{api_url}/carinfo/updateByVIN/{VIN}', data=_data, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f'Failed to send VIN return status code is {response.status_code}')
    else:
        print("Updated VIN on BACKEND!!!")


def sendSpeedTrigger(SPEED_LIMIT, SPEED, ROAD_NAME, Latitude, Longitude):
    _data = {}
    _data["username"] = "tirth"
    _data["SPEED"] = SPEED
    _data["ROAD_NAME"] = ROAD_NAME
    _data["SPEED_LIMIT"] = SPEED_LIMIT
    _data["Latitude"] = Latitude
    _data["Longitude"] = Longitude
    response = requests.post(f'http://{api_url}/speed-trigger/add', data=_data, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f'Failed to send speed Trigger return status code is {response.status_code}')
    else:
        print("Add SPEED Trigger on BACKEND!!!")