import obd
import threading
import time
import logging

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
        write_vals: int = 0

        if conn is None or not conn.is_connected():
            logger.error("No connection")
            write_vals = 0
            break

        if write_vals != 0:   # There is a connection, so proceed
            response_file = open('Local code/response.txt', 'a')

            ################################################################
            pid_val = 'ENGINE_LOAD'
            try:
                pid = getattr(obd.commands, pid_val)
            except AttributeError:
                print(f"{pid_val} is not valid")
                logger.error("PIDs didn't work")
                break
            response = conn.query(pid)

            if response.is_null():
                print("Failed to read PID:", pid)
                logger.error(f"Failed to read PID: {pid}")
            else:
                print("PID: ", pid, "Value: ", response.value)  # TODO: print to file
                returnedParamsValues.append((pid, response.value))
            ################################################################


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
    pid_thread = threading.Thread(target=readingPIDs_ins, args=('SPEED',))

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
