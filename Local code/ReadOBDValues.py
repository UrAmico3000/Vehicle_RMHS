import obd

conn = None

# 30 main params from OBD-II interface
listOfParams = ['RPM', 'SPEED', 'INTAKE_TEMP', 'THROTTLE_POS']  # TODO: research
# scratch - using mode01

returnedParamsValues = []  # this is then stored in the db

# Connect to the OBD-II interface
def connect():
    # Connect to the OBD-II interface
    global conn

    conn = obd.OBD(portstr='COM6', baudrate=38400)  # for rpi, use "/dev/ttyUSB0"

    # Check if the connection was successful
    if not conn.is_connected():
        print("Failed to connect to the OBD-II interface")
        exit()


def readingPIDs(pid_val):
    try:
        pid = getattr(obd.commands, pid_val)
    except:
        print(f"{pid_val} is not valid")

    response = conn.query(pid)

    if response.is_null():
        print("Failed to read PID:", pid)
    else:
        print("PID:", pid, "Value:", response.value)


def readingDTCs():
    # Read and print DTCs
    dtcs = conn.query(obd.commands.GET_DTC)
    if dtcs.is_null():
        print("Failed to read DTCs")
    else:
        for dtc in dtcs.value:
            print("DTC: " + dtc + "\n")


def main():
    # connect to OBD-II interface

    try:
        connect()
    except:
        print('error')

    # First read any DTCs
    # readingDTCs()
    # now reading params
    for val in listOfParams:
        print(readingPIDs(val))


    # Disconnect from the OBD-II interface
    conn.close()


if __name__ == "__main__":
    main()
