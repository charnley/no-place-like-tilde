
import models
from sqlalchemy.orm import sessionmaker

import location
import wingo_fiber

import requests

engine = models.db_connect()
Session = sessionmaker(bind=engine)


def update_avaliability():

    session = Session()
    exists = session.query(models.ApartmentModel).filter_by(available=None)

    for model in exists:

        url = model.url
        r = requests.get(url)

        if r.status_code == 404:
            model.available = "no"
            print(url, "no")
            session.commit()
        else:
            print(url)

    session.commit()

    return


def update_locations():

    session = Session()
    exists = session.query(models.ApartmentModel).filter_by(gps=None)

    for model in exists:

        pos = location.get_gps(model.address)

        if pos is None:
            continue

        model.gps = str(pos)

        print(model.id, model.gps)

    session.commit()

    return


def get_distance(model):

    gps = model.gps
    if gps is None:
        return None

    gps = eval(gps)
    dis = location.get_distance(gps)

    return dis


def update_internet(distance=None):

    session = Session()
    exists = session.query(models.ApartmentModel).filter_by(internet=None)

    for model in exists:

        address = wingo_fiber.get_address(model.address)

        if address:

            if distance is None: pass
            else:
                sbb_distance = get_distance(model)
                if sbb_distance is None: continue
                if sbb_distance > distance: continue

            result, message = wingo_fiber.check_address(address)

            if result:
                model.internet = result
            else:
                model.internet = "man"

            print("{:20d} {:} {:}".format(model.id, result, message))

    session.commit()

    return


def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='', metavar='file')
    parser.add_argument('--check_locations', action="store_true", help='')
    parser.add_argument('--check_internet', action="store_true", help='')
    parser.add_argument('--check_avaliable', action="store_true", help='')
    args = parser.parse_args()

    if args.check_locations:
        update_locations()

    if args.check_internet:
        update_internet(distance=2.0)

    if args.check_avaliable:
        update_avaliability()


    return

if __name__ == '__main__':
    main()
