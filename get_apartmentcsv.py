
import csv

import models
from models import ApartmentModel

from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, not_

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
        .filter(ApartmentModel.available == None) \
        .filter(ApartmentModel.rent <= 1700) \
        .filter(ApartmentModel.livingspace >= 40)

    for model in apartments:
        print(model)

    with open('apartments_dump.csv', 'w') as outcsv:

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

            # try:
            #     dis = location.get_distance(eval(model.gps))
            #     if dis > 2.0: continue
            # except:
            #     pass

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
