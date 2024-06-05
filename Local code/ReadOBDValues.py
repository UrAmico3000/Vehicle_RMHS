import obd
import threading
import time
import logging

FORMAT = '%(asctime)s - %(levelname)-10s: %(message)s'
logging.basicConfig(filename='ReadOBDValues.py.log', level=logging.ERROR, format=FORMAT)
conn = None

returnedParamsValues = []  # this is then stored in the db


# Connect to the OBD-II interface


def thread_5s():
    while True:
        time.sleep(5)
        print("Shabang")


def fd():
    while True:
        time.sleep(2)
        print("Testingggg")


def connect():
    # Connect to the OBD-II interface
    global conn
    conn = obd.OBD(portstr='COM6', baudrate=38400)  # for rpi, use "/dev/ttyUSB0"

    # Check if the connection was successful
    if not conn.is_connected():
        print("Failed to connect to the OBD-II interface")
        exit()


def readingPIDs_ins(pid_val):  # instantaneous
    while True:
        try:
            pid = getattr(obd.commands, pid_val)
        except:
            print(f"{pid_val} is not valid")
            logger = logging.getLogger('new_logs')
            logger.info("PIDs didn't work")

        response = conn.query(pid)

        if response.is_null():
            print("Failed to read PID:", pid)
        else:
            print("PID: ", pid, "Value: ", response.value)
        time.sleep(0.0)


def readingDTCs_5m():  # 5 mins
    # Read and print DTCs
    while True:
        dtcs = conn.query(obd.commands.GET_DTC)
        if dtcs.is_null():
            print("Failed to read DTCs")
        else:
            for dtc in dtcs.value:
                print("DTC: " + dtc + "\n")
        time.sleep(300.0)


def main():
    # connect to OBD-II interface
    try:
        connect()
    except Exception as e:
        print('Error in connection: ' + e.__cause__)
    finally:
        print('Moving ON')

    # Reading PIDs
    my_thread = threading.Thread(target=readingPIDs_ins, args={'pid'})

    # Reading DTCs every 15 minutes
    my_thread_2 = threading.Thread(target=readingDTCs_5m)

    # Threads initiation
    my_thread.start()

    my_thread_2.start()

    # command = obd.commands.modes
    # mode1_command = command[1]  # mode 1
    #
    # # Disconnect from the OBD-II interface
    # conn.close()


if __name__ == "__main__":
    main()
