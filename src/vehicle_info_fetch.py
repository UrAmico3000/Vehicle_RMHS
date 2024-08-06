import requests
import json


def set_vehicle_info():
    with open('VIN.txt', 'r') as file:
        vin = file.read().strip()

    # API URL with the VIN
    api_url = f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json'

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # Save the JSON data to a new file
        with open('decoded_vin.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Vehicle data updated from gov.")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
