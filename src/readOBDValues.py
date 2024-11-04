import obd
import threading
import time
import logging
import DataSend
import Gps
import MyLocation
import CommandList
import json

from collections import deque
import io
import sys
import vehicle_info_fetch as vf

# GPS import
import osmnx as ox
from shapely.geometry import Point
import requests


LOG_FORMAT = '%(asctime)s - %(levelname)-10s: %(message)s'
logging.basicConfig(filename='ReadOBDValues.py.log', level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('new_logs')

# variables
conn = None
PID_commands_list = []
command_queue = deque()
response_data_pid = {}
response_data_dtc = {}
# initial_FUEL_LEVEL = None

def set_PID_command_list():
    if vf.new_vehicle:
        print("New PID Command List:")
        pid_a = conn.query(obd.commands.PIDS_A)
        pid_b = conn.query(obd.commands.PIDS_B)
        pid_c = conn.query(obd.commands.PIDS_C)

        pid_a = pid_a.value
        pid_b = pid_b.value
        pid_c = pid_c.value

        for i in range(len(pid_a)):
            if(pid_a[i] == 1):
                CommandList.PID_A.append(i)
        for i in range(len(pid_b)):
            if(pid_b[i] == 1):
                CommandList.PID_B.append(i)
        for i in range(len(pid_c)):
            if(pid_c[i] == 1):
                CommandList.PID_C.append(i)

        jsonobject = {
            "pid_a":CommandList.PID_A,
            "pid_b":CommandList.PID_B,
            "pid_c":CommandList.PID_C,
        }
        with open('data.json', 'w') as f:
            json.dump(jsonobject, f)
    else:
        print("Same old vehicle")

# TODO Test it!!! :)
def fuelConsumption():
    first_level = True
    initial_FUEL_LEVEL = None
    trip_id = None
    initial_distance = None
    previous_speed = None
    total_distance_travelled = 0

    fuel_response = conn.query(obd.commands.FUEL_LEVEL)
    speed_response = conn.query(obd.commands.SPEED)  # Fetching the speed in km/h

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
    
def regular_queue_PIDs():
    while 1:
        for index in range(len(CommandList.Commands_A)):
            if index != 0 and (index in CommandList.PID_A):
                if CommandList.Commands_A[index] not in CommandList.PID_commands_list:
                    time.sleep(0.5) 
                    command_queue.append(CommandList.Commands_A[index])
        for index in range(len(CommandList.Commands_B)):
            if index != 0 and (index in CommandList.PID_B):
                if CommandList.Commands_B[index] not in CommandList.PID_commands_list:
                    time.sleep(0.5)
                    command_queue.append(CommandList.Commands_B[index])
        for index in range(len(CommandList.Commands_C)):
            if index != 0 and (index in CommandList.PID_C):
                if CommandList.Commands_C[index] not in CommandList.PID_commands_list:
                    time.sleep(0.5)
                    command_queue.append(CommandList.Commands_C[index])
        
   
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


def reading_DTCs_5m():  # 3 seconds
    while True:
        time.sleep(3)
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

def gps():
    G = ox.graph_from_place('Brampton, Ontario, Canada', network_type='drive')

    while True:
        my_location = Point(MyLocation.lng, MyLocation.lat)
        #nearest_node = ox.distance.nearest_nodes(G, X=my_location.x, Y=my_location.y)
        nearest_edge = ox.distance.nearest_edges(G, X=my_location.x, Y=my_location.y)

        edge_data = G.edges[nearest_edge]       # nearest edge on 'drive' map

        road_name = edge_data.get('name', 'unknown')
        speed_limit = edge_data.get('maxspeed', 50)

        if (MyLocation.lat != 0) and (MyLocation.lng != 0):
            print(f"Road name at location ({MyLocation.lat}, {MyLocation.lng}): {road_name}")
            print(f"Speed limit at location ({MyLocation.lat}, {MyLocation.lng}): {speed_limit}")
            if float(response_data_pid["SPEED"]) > float(speed_limit) + 10:
                print(f"you went over speed limit {speed_limit} with speed: {response_data_pid["SPEED"]}")
                # sends to backend
                DataSend.sendSpeedTrigger(float(speed_limit), float(response_data_pid["SPEED"]), road_name, MyLocation.lat ,MyLocation.lng)

        time.sleep(0.5)  # Pause for a while before checking the location again



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
    vehicle_info_fetch = vf.Vehicle_info_fetch(conn=conn,logger=logger)

    
    vehicle_info_fetch.check_vin()

    set_PID_command_list()
    CommandList.fetch_existing_values() # fetches json dump of supported PID values in index format

    ######################################################################################
    # threads down here

    # priority queue for reading PID values
    pid_thread = threading.Thread(target=reading_PIDs_ins)

    # Reading DTCs every 5 minutes
    dtc_thread = threading.Thread(target=reading_DTCs_5m)

    # Execute commands from queue
    execute_thread = threading.Thread(target=execute_commands)

    # Gps script
    gps_thread = threading.Thread(target=Gps.gps)

    # location thread
    location_thread = threading.Thread(target=MyLocation.my_location)

    # regular queue for reading PID values
    #longer_thread =  threading.Thread(target=regular_queue_PIDs)

    fuel_thread = threading.Thread(target=fuelConsumption)

    # Threads initiation
    pid_thread.start()
    dtc_thread.start()
    execute_thread.start()
    gps_thread.start()
    location_thread.start()
    #longer_thread.start()
    fuel_thread.start()

    # Awaiting their completion
    pid_thread.join()
    dtc_thread.join()
    execute_thread.join()
    gps_thread.join()
    location_thread.join()
    #longer_thread.join()
    fuel_thread.join()
    ######################################################################################


if __name__ == "__main__":
    main()
