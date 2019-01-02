
import models
from sqlalchemy.orm import sessionmaker

import location
import wingo_fiber

engine = models.db_connect()
Session = sessionmaker(bind=engine)

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


def update_internet():

    session = Session()
    exists = session.query(models.ApartmentModel).filter_by(internet=None)

    for model in exists:

        address = wingo_fiber.get_address(model.address)

        if address:

            result, message = wingo_fiber.check_address(address)

            if result:

                model.internet = result

            else:

                model.internet = "man"

            print(model.id, result, message)

    session.commit()

    return


def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='', metavar='file')
    args = parser.parse_args()


    update_locations()
    update_internet()

    return

if __name__ == '__main__':
    main()
