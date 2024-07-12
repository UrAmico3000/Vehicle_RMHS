import osmnx as ox
from shapely.geometry import Point

latitude = 43.65852
longitude = -79.73235

# Download and parse OSM data for Brampton, Ontario
G = ox.graph_from_place('Brampton, Ontario, Canada', network_type='drive')

my_location = Point(longitude, latitude)

nearest_node = ox.distance.nearest_nodes(G, X=my_location.x, Y=my_location.y)

nearest_edge = ox.distance.nearest_edges(G, X=my_location.x, Y=my_location.y)

edge_data = G.edges[nearest_edge]

# Get the road name
road_name = edge_data.get('name', 'unknown')

# Get the speed limit
speed_limit = edge_data.get('maxspeed', 'unknown')

# Print the road name and speed limit
print(f"Road name at location ({latitude}, {longitude}): {road_name}")
print(f"Speed limit at location ({latitude}, {longitude}): {speed_limit}")