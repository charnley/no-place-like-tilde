
import csv

import models
from models import ApartmentModel
from sqlalchemy.orm import sessionmaker

import location
import wingo_fiber

engine = models.db_connect()
Session = sessionmaker(bind=engine)


def main():

    # exists = session.query(models.ApartmentModel).filter_by(livingspace=None)

    # 2-3 rooms
    # below 1500
    # min 50 m2
    # fiber internet

    session = Session()
    apartments = session.query(ApartmentModel) \
        .filter(ApartmentModel.livingspace >= 45) \
        .filter(ApartmentModel.internet == "success") \
        .filter(ApartmentModel.rent <= 1600)

    for model in apartments:
        print(model)

    with open('angela.csv', 'w') as outcsv:

        header = [
            'id',
            'internet',
            'address',
            'gps',
            'rent',
            'squarementer',
            'rooms',
            'url']

        writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(header)

        for model in apartments:
            writer.writerow([
                model.id,
                model.internet,
                model.address,
                model.gps,
                model.rent,
                model.livingspace,
                model.rooms,
                model.url])



    return

if __name__ == '__main__':
    main()
