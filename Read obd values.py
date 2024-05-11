import obd


def main():
    # Connect to the OBD-II interface
    connection = obd.OBD()

    # Check if the connection was successful
    if not connection.is_connected():
        print("Failed to connect to the OBD-II interface")
        exit()

    # Read and print a specific PID
    pid = obd.commands.RPM
    response = connection.query(pid)
    if response.is_null():
        print("Failed to read PID:", pid)
    else:
        print("PID:", pid, "Value:", response.value)

    # Read and print all available PIDs
    pids = obd.commands.ALL
    response = connection.query(pids)
    if response.is_null():
        print("Failed to read PIDs:", pids)
    else:
        for pid, value in response.value.items():
            print("PID:", pid, "Value:", value)

    # Read and print DTCs
    dtcs = connection.query(obd.commands.GET_DTC)
    if dtcs.is_null():
        print("Failed to read DTCs")
    else:
        for dtc in dtcs.value:
            print("DTC:", dtc)

    # Disconnect from the OBD-II interface
    connection.close()

# Connect to the OBD-II interface
connection = obd.OBD()


if __name__ == "__main__":
    main()
