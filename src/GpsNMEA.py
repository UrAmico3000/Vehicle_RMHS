import pynmea2
import serial

while True:
    port = "/dev/ttyAMAO"
    ser = serial.Serial(port, baudrate=9600, timeout=0.5)
    data_out = pynmea2.NMEAStreamReader()
    new_data = ser.readline()
    if new_data[0:6] == "$GPRMC":
        new_msg = pynmea2.parse(new_data)
        lat = new_msg.latitude
        lng = new_msg.longitude
        gps = "Latitude=" + str(lat) + "and Longitude = " + str(lng)

    print(gps)