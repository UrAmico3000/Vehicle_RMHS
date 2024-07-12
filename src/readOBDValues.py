import obd
import threading
import time
import logging
import json
import src.DataSend
from collections import deque

LOG_FORMAT = '%(asctime)s - %(levelname)-10s: %(message)s'
logging.basicConfig(filename='ReadOBDValues.py.log', level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('new_logs')
conn = None
api_url = ""
command_queue = deque()
response_data = {}
current_DTC = []


# Connect to the OBD-II interface
def connect():
    # Connect to the OBD-II interface
    global conn
    conn = obd.OBD(portstr="/dev/ttyUSB0", baudrate=38400)  # for rpi, use "/dev/ttyUSB0"

    # Check if the connection was successful
    if not conn.is_connected():
        logger.error("Failed to connect to the OBD-II interface")
        raise Exception("Failed to connect to the OBD-II interface")


def readingPIDs_ins():  # instantaneous
    commands = [
        obd.commands.RPM,  # Engine RPM
        obd.commands.SPEED,  # Vehicle Speed
        obd.commands.ENGINE_LOAD,
        obd.commands.LONG_FUEL_TRIM_1,
        obd.commands.O2_B1S1,
        obd.commands.THROTTLE_POS,  # Throttle Position
        obd.commands.COOLANT_TEMP,  # Coolant Temperature
        obd.commands.MAF,  # Mass Air Flow
        obd.commands.FUEL_LEVEL  # Fuel Level
    ]

    while True:
        for pid_val in commands:
            command_queue.append(pid_val)
        time.sleep(0.4)  # Adjust the delay as needed
        src.sendPIDvalues(response_data)  # sending data


def readingDTCs_5m():  # 5 mins
    while True:
        if conn is None or not conn.is_connected():
            logger.error("OBD-II connection is not established")
            break

        command_queue.append(obd.commands.GET_DTC)
        time.sleep(1)


def executeCommands():
    while True:
        if command_queue:
            command_val = command_queue.popleft()
            response_data = {}

            response = conn.query(command_val)
            if response.is_null():
                logger.error(f"Failed to read PID: {command_val}")
                response_data[command_val] = None
            elif command_val.name == 'GET_DTC':
                current_DTC = response.value
                print("GET_DTC EXECUTED - current dtcs: " + str(current_DTC))
            else:
                response_data[command_val.name] = response.value.magnitude
                print("Response for command " + command_val.name + " is :" + str(response.value.magnitude))

            # print("Response for command "+ command_val.name)
            # with open('response.json', 'a') as response_file:
            # response_file.write(json.dumps(response_data) + "\n")


def main():
    global api_url

    # Load the configuration file
    with open('../config.json', 'r') as config_file:
        config = json.load(config_file)

    # Access the API_URL
    api_url = config['API_URL']
    # connect to OBD-II interface
    try:
        connect()
    except Exception as e:
        logger.error('Error in connection: ', exc_info=True)
        print('Error in connection:', e)
        return  # Exit the program if connection fails
    finally:
        print('-----Moving ON-----')

        # this is for UI but for some reason cant get it to launch in fullscreen in rpi works fine in Ubuntu or windows
        # unfortunately this sits in main thread
        # eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])

    # Reading PIDs
    pid_thread = threading.Thread(target=readingPIDs_ins)

    # Reading DTCs every 5 minutes
    dtc_thread = threading.Thread(target=readingDTCs_5m)

    # Execute commands from queue
    execute_thread = threading.Thread(target=executeCommands)

    # Threads initiation
    pid_thread.start()
    dtc_thread.start()
    execute_thread.start()

    # Awaiting their completion
    pid_thread.join()
    dtc_thread.join()
    execute_thread.join()


if __name__ == "__main__":
    main()
