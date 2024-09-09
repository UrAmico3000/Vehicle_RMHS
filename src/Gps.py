import osmnx as ox
import MyLocation
import time
# from MyLocation import lat, lng
from shapely.geometry import Point
import readOBDValues
import DataSend


########################################################################################

# using urllib3==1.26.15 will work only on linux environments, the latest version will work too but will give off ssl
# errors; Scikit-learn is also a necessity to run urllib - added to requirements

########################################################################################

def gps():
    G = ox.graph_from_place('Brampton, Ontario, Canada', network_type='drive')

    while True:
        my_location = Point(MyLocation.lng, MyLocation.lat)
        #nearest_node = ox.distance.nearest_nodes(G, X=my_location.x, Y=my_location.y)
        nearest_edge = ox.distance.nearest_edges(G, X=my_location.x, Y=my_location.y)

        edge_data = G.edges[nearest_edge]       # nearest edge on 'drive' map

        road_name = edge_data.get('name', 'unknown')
        speed_limit = edge_data.get('maxspeed', 50)

        if (MyLocation.lat != 0) and (MyLocation.lng != 0):
            print(f"Road name at location ({MyLocation.lat}, {MyLocation.lng}): {road_name}")
            print(f"Speed limit at location ({MyLocation.lat}, {MyLocation.lng}): {speed_limit}")
            if readOBDValues.response_data_pid["SPEED"] > speed_limit + 2:
                print(f"you went over speed limit {speed_limit} with speed: {readOBDValues.response_data_pid["SPEED"]}")
                # sends to backend
                DataSend.sendSpeedTrigger(speed_limit, readOBDValues.response_data_pid["SPEED"], road_name, MyLocation.lat ,MyLocation.lng)

        time.sleep(0.5)  # Pause for a while before checking the location again
