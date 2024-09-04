import requests
import json

VIN = None
new_vehicle = False

class Vehicle_info_fetch:
    def __init__(self, conn, logger):
        self.conn = conn
        self.logger = logger
        
    def get_vin(self):
        from obd import obd
        vin_cmd = obd.commands.VIN
        vin_response = self.conn.query(vin_cmd)
        if vin_response:
            return vin_response.value
        return None


    def check_vin(self):
        global VIN
        VIN = self.get_vin()
        VIN = VIN.decode('ascii', errors='replace')
        print(f'VIN IS : {VIN}')
        with open(file='VIN.txt',mode='r+') as f:
            _current_vin = f.read()

            # Update if a new one 
            if _current_vin != VIN:
                global new_vehicle
                new_vehicle = True
                print("new Vehicle")
                
                f.write(VIN)
                print("VIN updated successfully...")
                self.logger.info("Updated VIN: " + VIN)

                # i am in car with tirth so you do reorganizing later!!!!
                import DataSend
                DataSend.sendVIN(VIN)
                print("Vehicle info updated successfully...")

                f.close()
                return
            else:
                f.close()
                return

