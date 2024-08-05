import obd
import threading
import time
import logging
import DataSend
import Gps
import MyLocation
import new_car_or_not_logic
from collections import deque

LOG_FORMAT = '%(asctime)s - %(levelname)-10s: %(message)s'
logging.basicConfig(filename='ReadOBDValues.py.log', level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('new_logs')

# variables
conn = None
PID_commands_list = []
command_queue = deque()
response_data_pid = {}
response_data_dtc = {}


# Connect to the OBD-II interface
def connect():
    # Connect to the OBD-II interface
    global conn
    conn = obd.OBD(portstr="/dev/ttyUSB0", baudrate=38400)  # for rpi, use "/dev/ttyUSB0"

    # Check if the connection was successful
    if not conn.is_connected():
        logger.error("Failed to connect to the OBD-II interface")
        raise Exception("Failed to connect to the OBD-II interface")
    else:
        print('-----CONNECTION ESTABLISHED-----')


def init():

    # connect to OBD-II interface
    try:
        connect()
    except Exception as e:
        logger.error('Error in connection: ', exc_info=True)
        print('Error in connection:', e)
        return  # Exit the program if connection fails


def reading_PIDs_ins():  # instantaneous
    global PID_commands_list

    # PID_commands_list = [
    #     obd.commands.RPM,  # Engine RPM
    #     obd.commands.SPEED,  # Vehicle Speed
    #     obd.commands.ENGINE_LOAD,
    #     obd.commands.LONG_FUEL_TRIM_1,
    #     obd.commands.O2_B1S1,
    #     obd.commands.THROTTLE_POS,  # Throttle Position
    #     obd.commands.COOLANT_TEMP,  # Coolant Temperature
    #     obd.commands.MAF,  # Mass Air Flow
    #     obd.commands.FUEL_LEVEL  # Fuel Level
    # ]

    # looping through all commands - sending
    while True:
        for pid_val in PID_commands_list:
            command_queue.append(pid_val)
        time.sleep(0.5)  # Adjust the delay as needed
        DataSend.send_PID_values(response_data_pid)  # Updating data on api_url


def reading_DTCs_5m():  # 5 mins
    while True:
        time.sleep(300)
        if conn is None or not conn.is_connected():
            logger.error("OBD-II connection is not established")
            break

        command_queue.append(obd.commands.GET_DTC)

        DataSend.send_DTC_values(response_data_dtc)  # Updating data on api_url


def execute_commands():
    global response_data_dtc
    global response_data_pid
    while True:
        if command_queue:
            current_queried_command = command_queue.popleft()

            response = conn.query(current_queried_command)
            if response.is_null():
                logger.error(f"Failed to read PID: {current_queried_command}")
                response_data_pid[current_queried_command] = None

            elif current_queried_command.name == 'GET_DTC':
                response_data_dtc = response.value  # or response.value.magnitude
                print("GET_DTC EXECUTED - current dtcs: " + str(response_data_dtc))

            else:
                response_data_pid[current_queried_command.name] = response.value.magnitude
                print("Response for command " + current_queried_command.name + " is :" + str(response.value.magnitude))

            # print("Response for command "+ command_val.name)
            # with open('response.json', 'a') as response_file:
            # response_file.write(json.dumps(response_data) + "\n")


def main():
    ###################################################################
    # this is for UI but for some reason cant get it to launch in
    # full-screen in rpi works fine in Ubuntu or windows
    # unfortunately this sits in main thread
    # eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])
    ###################################################################

    # Initialize - url and odb connection
    init()

    # New Car check

    new_car_or_not_logic.check_vin()

    ######################################################################################
    # threads down here

    # Reading PIDs
    pid_thread = threading.Thread(target=reading_PIDs_ins)

    # Reading DTCs every 5 minutes
    dtc_thread = threading.Thread(target=reading_DTCs_5m)

    # Execute commands from queue
    execute_thread = threading.Thread(target=execute_commands)

    # Gps script
    gps_thread = threading.Thread(target=Gps.gps)

    # location thread
    location_thread = threading.Thread(target=MyLocation.my_location)

    # Threads initiation
    pid_thread.start()
    dtc_thread.start()
    execute_thread.start()
    gps_thread.start()
    location_thread.start()

    # Awaiting their completion
    pid_thread.join()
    dtc_thread.join()
    execute_thread.join()
    gps_thread.join()
    location_thread.join()
    ######################################################################################


if __name__ == "__main__":
    main()
