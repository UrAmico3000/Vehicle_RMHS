import obd
import threading
import time
import logging
import json

LOG_FORMAT = '%(asctime)s - %(levelname)-10s: %(message)s'
logging.basicConfig(filename='ReadOBDValues.py.log', level=logging.ERROR, format=LOG_FORMAT)
logger = logging.getLogger('new_logs')
conn = None

returnedParamsValues = []  # this is then stored in the db


# Connect to the OBD-II interface
def connect():
    # Connect to the OBD-II interface
    global conn
    conn = obd.OBD(portstr='COM6', baudrate=38400)  # for rpi, use "/dev/ttyUSB0"

    # Check if the connection was successful
    if not conn.is_connected():
        logger.error("Failed to connect to the OBD-II interface")
        raise Exception("Failed to connect to the OBD-II interface")


def readingPIDs_ins():  # instantaneous
    while True:
        if conn is None or not conn.is_connected():
            logger.error("No connection")
            break

        response_data = {}
        pids_to_read = [
            'ENGINE_LOAD', 'COOLANT_TEMP', 'RPM', 'MAF', 'THROTTLE_POS',
            'SHORT_FUEL_TRIM_1', 'LONG_FUEL_TRIM_1', 'FUEL_PRESSURE',
            'TIMING_ADVANCE', 'O2_B1S1'
        ]

        for pid_val in pids_to_read:
            try:
                pid = getattr(obd.commands, pid_val)
            except AttributeError:
                print(f"{pid_val} is not valid")
                logger.error(f"PID {pid_val} didn't work")
                continue

            response = conn.query(pid)

            if response.is_null():
                print(f"Failed to read PID: {pid_val}")
                logger.error(f"Failed to read PID: {pid_val}")
                response_data[pid_val] = None
            else:
                # Validate the response value
                if isinstance(response.value, (int, float)):
                    print(f"PID: {pid_val}, Value: {response.value}")
                    response_data[pid_val] = response.value
                else:
                    print(f"Invalid data for PID: {pid_val}")
                    logger.error(f"Invalid data for PID: {pid_val}")
                    response_data[pid_val] = None

        returnedParamsValues.append(response_data)

        with open('Local code/response.json', 'a') as response_file:
            response_file.write(json.dumps(response_data) + "\n")

        time.sleep(0.5)  # Added a slight delay to prevent excessive querying


def readingDTCs_5m():  # 5 mins
    # Read and print DTCs
    while True:
        if conn is None or not conn.is_connected():
            logger.error("OBD-II connection is not established")
            break

        dtcs = conn.query(obd.commands.GET_DTC)
        if dtcs.is_null():
            print("Failed to read DTCs")
            logger.error("Failed to read DTCs")
        else:
            for dtc in dtcs.value:
                print("DTC: " + dtc)
                returnedParamsValues.append(("DTC", dtc))
        time.sleep(300.0)


def main():
    # connect to OBD-II interface
    try:
        connect()
    except Exception as e:
        logger.error('Error in connection: ', exc_info=True)
        print('Error in connection:', e)
        return  # Exit the program if connection fails
    finally:
        print('-----Moving ON-----')

    # Reading PIDs
    pid_thread = threading.Thread(target=readingPIDs_ins)

    # Reading DTCs every 5 minutes
    dtc_thread = threading.Thread(target=readingDTCs_5m)

    # TODO: Another thread for remote database update

    # Threads initiation
    pid_thread.start()
    dtc_thread.start()

    # Awaitingg their completion
    pid_thread.join()
    dtc_thread.join()


if __name__ == "__main__":
    main()