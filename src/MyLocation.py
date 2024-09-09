import pynmea2
import serial

_port = "/dev/ttyACM0"
lat = 0  # Using yours as a default for now
lng = 0


def my_location():
    global lat, lng

    try:
        _ser = serial.Serial(_port, baudrate=9600, timeout=0.5)
        _data_out = pynmea2.NMEAStreamReader()  # redundant nigga?
    except Exception as e:
        print("Error opening serial port: ", e)
        return lat, lng

    while True:
        try:
            new_data = _ser.readline().decode('ascii', errors='replace')  # Ensure new_data is a string
        except Exception as e:
            print("Error reading from serial port: ", e)
            print("Trying again in 5 seconds... ")
            continue

        if new_data.startswith("$GPRMC") or type(new_data) is not str or new_data is None:
            try:
                new_msg = pynmea2.parse(new_data)
                lat = new_msg.latitude
                lng = new_msg.longitude
                gps = f"Latitude = {lat} and Longitude = {lng}"
                print(gps)
            except pynmea2.ParseError as e:
                print("Parse error: ", e)

    _ser.close()  # idk if needed
