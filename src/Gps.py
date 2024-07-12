import osmnx as ox
import src.MyLocation
import time
# from MyLocation import lat, lng
from shapely.geometry import Point


########################################################################################

# using urllib3==1.26.15 will work only on linux environments, the latest version will work too but will give off ssl
# errors; Scikit-learn is also a necessity to run urllib - added to requirements

########################################################################################

def Gps():
    G = ox.graph_from_place('Brampton, Ontario, Canada', network_type='drive')

    # Starting the loop for getting continuous location
    src.MyLocation()

    while True:
        my_location = Point(src.MyLocation.lng, src.MyLocation.lat)
        nearest_node = ox.distance.nearest_nodes(G, X=my_location.x, Y=my_location.y)
        nearest_edge = ox.distance.nearest_edges(G, X=my_location.x, Y=my_location.y)

        edge_data = G.edges[nearest_edge]       # nearest edge on 'drive' map

        road_name = edge_data.get('name', 'unknown')
        speed_limit = edge_data.get('maxspeed', 'unknown')

        print(f"Road name at location ({src.MyLocation.lat}, {src.MyLocation.lng}): {road_name}")
        print(f"Speed limit at location ({src.MyLocation.lat}, {src.MyLocation.lng}): {speed_limit}")

        time.sleep(10)  # Pause for a while before checking the location again
