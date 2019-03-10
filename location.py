
import geopy

from geopy.distance import geodesic
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="specify_your_app_name_here")


def get_gps(address):
    """

    """

    address = address.split(",")
    address[0] = address[0].split("/")[0]
    address[0] = address[0].split("(")[0]
    address = ",".join(address)

    location = geolocator.geocode(address)

    if location is None:
        return None

    address = location.address
    gps = location.latitude, location.longitude

    return gps


def get_distance(a, b=(47.547639, 7.589852)):
    distance = geodesic(a, b).km
    return distance


def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='', metavar='file')
    args = parser.parse_args()

    pos = get_gps("Wettsteinplatz 3, 4058 Basel")
    print(pos)
    print("sbb", get_distance(pos))

    pos = get_gps("Luzernerring 85, 4056 Basel")
    print(pos)
    print("sbb", get_distance(pos))

    return

if __name__ == '__main__':
    main()


