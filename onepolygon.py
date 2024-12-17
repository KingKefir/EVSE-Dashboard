import geojson
from shapely.geometry import shape, Point

# Load GeoJSON file containing the polygon
def load_geojson(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        data = geojson.load(f)
    return data

geojson_file = "data_hamburg/app_bezirke_EPSG_4326.json"  # Replace with your GeoJSON file path
geojson_data = load_geojson(geojson_file)

polygon = None
for feature in geojson_data['features']:
    if feature['geometry']['type'] == 'MultiPolygon':
        polygon = shape(feature['geometry'])  # Convert to Shapely Polygon
        print(feature['properties']['bezirk_name'])
        # print(polygon.type)