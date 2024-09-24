import obd
import threading
import time
import logging
import datetime

import requests

import DataSend
import Gps
import MyLocation
import CommandList
import json

from collections import deque
import io
import sys
import vehicle_info_fetch as vf

LOG_FORMAT = '%(asctime)s - %(levelname)-10s: %(message)s'
logging.basicConfig(filename='ReadOBDValues.py.log', level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('new_logs')

# variables
conn = None
PID_commands_list = []
command_queue = deque()
response_data_pid = {}
response_data_dtc = {}

DIST_TRAVELLED = 0


# initial_FUEL_LEVEL = None

def set_PID_command_list():
    def process_pid_data(pid_data, command_list):
        for i, value in enumerate(pid_data):
            if value == 1:
                command_list.append(i)

    if vf.new_vehicle:
        print("New PID Command List:")
        pid_a = conn.query(obd.commands.PIDS_A).value
        pid_b = conn.query(obd.commands.PIDS_B).value
        pid_c = conn.query(obd.commands.PIDS_C).value

        # Process each PID list and append valid commands
        process_pid_data(pid_a, CommandList.PID_A)
        process_pid_data(pid_b, CommandList.PID_B)
        process_pid_data(pid_c, CommandList.PID_C)

        jsonobject = {
            "pid_a": pid_a,
            "pid_b": pid_b,
            "pid_c": pid_c,
        }

        with open('data.json', 'w') as f:
            json.dump(jsonobject, f)
    else:
        print("Same old vehicle 😇")


# def fuelConsumption():
#     first = True
#     while 1:
#         if first:
#             pass;
#         else:
#             send Backend (response_data_pid["FUEL_LEVEL"] - initial_FUEL_LEVEL) # delta on disconnect
#         first =  False

def fuelConsumption(connection):
    first_level = True
    initial_FUEL_LEVEL = None
    trip_id = None
    initial_distance = None
    previous_speed = None
    total_distance_travelled = 0

    fuel_response = connection.query(obd.commands.FUEL_LEVEL)
    speed_response = connection.query(obd.commands.SPEED)  # Fetching the speed in km/h

    while True:
        current_FUEL_LEVEL = fuel_response.value.magnitude if not fuel_response.is_null() else None
        current_speed = speed_response.value.magnitude if not speed_response.is_null() else None  # in km/h

        if current_FUEL_LEVEL is None:
            print("Fuel level data not available")
            continue

        if current_speed is None:
            print("Speed data not available")
            continue

        if first_level:
            # Initialize the fuel level and set initial values
            initial_FUEL_LEVEL = current_FUEL_LEVEL
            previous_speed = current_speed

            # Backend trip initiation
            response = requests.post(f"http://{DataSend.api_url}/trip/add",
                                     json={"username": "Tirth"})
            trip_data = response.json()
            trip_id = trip_data.get("id")

            first_level = False
        else:
            # Calculate distance using the speed formula: distance = speed * time
            time_elapsed_hours = 5 / 3600  # 5 seconds converted to hours
            distance_travelled = previous_speed * time_elapsed_hours  # Distance in km
            total_distance_travelled += distance_travelled  # Accumulating the total distance

            fuel_consumed = initial_FUEL_LEVEL - current_FUEL_LEVEL

            data = {
                "FuelConsumption": fuel_consumed,
                "DistanceTravelled": total_distance_travelled
            }

            try:
                response = requests.put(f"http://{DataSend.api_url}/trip/update/{trip_id}", json=data)
                response.raise_for_status()
                print("Trip updated successfully")
            except requests.exceptions.RequestException as e:
                print(f"Error updating trip: {e}")

            # Update the previous speed for the next calculation
            previous_speed = current_speed

        # Delay for 5 seconds before the next update
        time.sleep(5)


# def query_distance_travelled(connection):
#     dist = connection.query.obd.commands.DISTANCE_SINCE_DTC_CLEAR
#     meh = 10
#     return meh


# Average Fuel Consumption Last month Consumption
# last trip
# fuel consumption * price ()
# Trip on Monday from Eglinton to Burlington
# Co2 emission 


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


def process_commands(commands, pid_list):
    for index in range(len(commands)):
        if index != 0 and (index in pid_list):
            if commands[index] not in CommandList.PID_commands_list:
                time.sleep(0.5)
                command_queue.append(commands[index])


def regular_queue_PIDs():
    while 1:
        process_commands(CommandList.Commands_A, CommandList.PID_A)
        process_commands(CommandList.Commands_B, CommandList.PID_B)
        process_commands(CommandList.Commands_C, CommandList.PID_C)


# def loop():
#     for index in range(len(CommandList.Commands_A)):
#         if index != 0 and (index in CommandList.PID_A):
#             if CommandList.Commands_A[index] not in CommandList.PID_commands_list:
#                 time.sleep(0.5)
#                 command_queue.append(CommandList.Commands_A[index])

def reading_PIDs_ins():  # instantaneous
    global PID_commands_list

    PID_commands_list = [
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
                if conn.supports(current_queried_command):
                    response_data_pid[current_queried_command.name] = response.value.magnitude
                else:
                    # TODO Check if it works
                    if current_queried_command in CommandList.Commands_A:
                        CommandList.PID_A.remove(CommandList.Commands_A.index(current_queried_command))
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

    # Initialize - url and obd connection
    init()

    # New Car check
    vehicle_info_fetch = vf.Vehicle_info_fetch(conn=conn, logger=logger)
    vehicle_info_fetch.check_vin()

    set_PID_command_list()  # setting the list by seeing which one works and which ones don't
    CommandList.fetch_existing_values()  # fetches json dump of supported PID values in index format

    ######################################################################################
    # threads down here

    # priority queue for reading PID values
    pid_priority_thread = threading.Thread(target=reading_PIDs_ins)

    # regular queue for reading PID values
    pid_regular_thread = threading.Thread(target=regular_queue_PIDs)

    # Reading DTCs every 5 minutes
    dtc_thread = threading.Thread(target=reading_DTCs_5m)

    # Execute commands from queue
    execute_thread = threading.Thread(target=execute_commands)

    # Gps script
    gps_thread = threading.Thread(target=Gps.gps)

    # location thread
    location_thread = threading.Thread(target=MyLocation.my_location)

    # Threads initiation
    pid_priority_thread.start()
    dtc_thread.start()
    execute_thread.start()
    gps_thread.start()
    location_thread.start()
    pid_regular_thread.start()

    # Awaiting their completion
    pid_priority_thread.join()
    dtc_thread.join()
    execute_thread.join()
    gps_thread.join()
    location_thread.join()
    pid_regular_thread.join()
    ######################################################################################


if __name__ == "__main__":
    main()
