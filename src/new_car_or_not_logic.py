import readOBDValues


def get_vin():
    from obd import obd
    vin_cmd = obd.commands.VIN
    vin_response = readOBDValues.conn.query(vin_cmd)
    if vin_response.is_successful():
        return vin_response.value
    return None


def check_vin():
    global VIN
    VIN = get_vin()
    with open(file='VIN.txt') as f:
        _current_vin = f.read()

        # Update if a new one
        if _current_vin != VIN:
            f.write(VIN)
            print("VIN updated successfully")
            readOBDValues.logger.info("Updated VIN: " + VIN)
            f.close()
        else:
            print("Failed to retrieve VIN")
            readOBDValues.logger.error("Could not update VIN")
