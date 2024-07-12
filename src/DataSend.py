from src.readOBDValues import api_url
import requests
import json


def sendPIDvalues(PID):
    data = PID
    data["username"] = "tirth"
    print(f'http://{api_url}/sensor/set and data is {data}')
    json_object = json.dumps(data, indent=4)
    response = requests.post(f'http://{api_url}/sensor/set', data=json_object, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f'Failed to send return status code is {response.status_code}')