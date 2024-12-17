import geojson
import requests
from shapely.geometry import shape, Point

# Load GeoJSON file containing the polygon
def load_geojson(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        data = geojson.load(f)
    return data

# Fetch SensorThings locations from OGC API
def fetch_sensorthings_locations(api_url):
    sensor_points = {}
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Parse SensorThings data (assuming 'value' is a list of Location entries)
        for item in data.get('value', []):
            sensor_id = item.get('@iot.id')  # Unique SensorThings ID
            coordinates = item['location']['geometry']['coordinates']  # GeoJSON format: [longitude, latitude]
            sensor_points[f"Sensor_{sensor_id}"] = tuple(coordinates)

        return sensor_points
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return {}

# Check if SensorThings points are within the GeoJSON polygon
def check_points_in_polygon(geojson_data, sensor_points):
    # Extract the first polygon in the GeoJSON file
    # TODO Trage die Sensoren in eine Liste mit den Entsprechenden Bezirken ein.
    # TODO In welchem feature befindet die sensor_points

    polygons = []
    for feature in geojson_data['features']:
        if feature['geometry']['type'] == 'MultiPolygon':
            polygons.append(shape(feature['geometry']))
            bezirk = feature['properties']['bezirk_name']

    if not polygons:
        raise ValueError("No polygon found in the provided GeoJSON file")

    # Check if the SensorThings points are within the polygon
    results = []
    for point_id, coords in sensor_points.items():
        point = Point(coords)  # Create a Shapely point
        inside_any = any(polygon.contains(point) for polygon in polygons)  # Check all polygons
        results.append((point_id, coords, inside_any, bezirk))
    
    return results

# Example usage
if __name__ == "__main__":
    # Path to your GeoJSON file
    geojson_file = "data_hamburg/app_bezirke_EPSG_4326.json"  # Replace with your GeoJSON file path
    geojson_data = load_geojson(geojson_file)

    # OGC SensorThings API URL
    # Filter in URL liefert ausschliesslich EVSE zurück.
    # sensorthings_api_url = "https://iot.hamburg.de/v1.1/Locations?$filter=substringof('E-Ladestation', name)&$skip=1000" # Replace with your API URL
    sensorthings_api_url = "https://iot.hamburg.de/v1.1/Locations?$filter=substringof('E-Ladestation', name)" # Replace with your API URL
    
    # Fetch SensorThings data from the API
    sensor_points = fetch_sensorthings_locations(sensorthings_api_url)
    if not sensor_points:
        print("No sensor data fetched. Exiting.")
        exit()

    # Check which points are inside the polygon
    results = check_points_in_polygon(geojson_data, sensor_points)

    # Print the results
    for point_id, coords, is_within, bezirk in results:
    # for point_id, coords, is_within in results:
        status = "inside" if is_within else "outside"
        print(f"Sensor '{point_id}' with coordinates {coords} is {status} the polygon. BEZIRK: {bezirk}")
        # print(f"Sensor '{point_id}' with coordinates {coords} is {status} the polygon.")

        # if is_within:
        #     print(f"Sensor '{point_id}' with coordinates {coords} is inside the polygon. BEZIRK: {bezirk} ")