import random
import json


class OBDReader:
    def __init__(self):
        # Initialization for OBD connection (serial, etc.)
        pass

    def get_json_data(self):
        # Simulate getting a JSON string from OBD-II (replace with actual OBD-II fetching)
        data = {
            'rpm': random.randint(0, 8000),  # Simulated value, replace with actual OBD data
            'speed': random.randint(0, 200)  # Simulated value, replace with actual OBD data
        }
        return json.dumps(data)  # Return as a JSON string
