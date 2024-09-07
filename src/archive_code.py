



## harsh's code for reference

def extract_command_names(conn):
    commands_list = []

    # Capture the print output of conn.print_commands
    captured_output = io.StringIO()  # Create StringIO object
    sys.stdout = captured_output  # Redirect stdout to the StringIO object

    conn.print_commands()  # Call the method to print commands

    sys.stdout = sys.__stdout__  # Reset redirect.

    commands_output = captured_output.getvalue()  # Get the printed output as a string

    # Process each line of the captured output
    for line in commands_output.strip().split("\n"):
        parts = line.strip().split("] ")
        if len(parts) == 2:
            command_name = parts[1].strip().replace(" ", "_").upper()
            commands_list.append(f"obd.commands.{command_name}")

    return commands_list


def set_PID_command_list():  # will run only if VIN is changed
    # ------------- pseudo code -------------- ########################################################
    # if new_vehicle:
    #     # run PID_A commands
    #     # get values and store in the variable 'available_commands_b' in binary
    #     # loop init
    #     # for each of the 1s in the binary response available_commands_b, get the
    #     # response.name for the corresponding commands
    #     # ... and further store it in the format - obd.commands.command_name (RPM for instance)
    #     # append it to the list
    #     # next iteration until it ends
    #
    #     readOBDValues.PID_commands_list = []
    ###################################################################################################

    global new_vehicle
    if new_vehicle:
        #PID_commands_list = extract_command_names(conn)

        # TODO: a) or try any other method to convert to bitstring, if it does not work
        # # Run PID_A commands to get the list of supported PIDs
        # pid_A_command = obd.commands.PIDS_A
        # response = readOBDValues.conn.query(pid_A_command)
        #
        # if response.is_successful():
        #     # Get the binary string of the response
        #     available_commands_b = response.value.bitstring
        #
        #     # Iterate over each bit in the binary string
        #     for i, bit in enumerate(available_commands_b):
        #         if bit == '1':
        #             # Get the corresponding command based on the index
        #             command = obd.commands[pid_A_command[i + 1]]
        #             readOBDValues.PID_commands_list.append(command)

        # TODO: b) either comment out the the above and try the following
        print("New PID Command List:")
        for command in PID_commands_list:  # just to see commands yk
            print(command)

        # Reset the new_vehicle flag
        new_vehicle = False
        return

    print("Same old vehicle - mehhh...")
    return