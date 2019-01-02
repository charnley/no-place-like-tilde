
import matplotlib as mpl
import matplotlib.pyplot as plt

import csv

import models
from models import ApartmentModel
from sqlalchemy.orm import sessionmaker

import location
import wingo_fiber

engine = models.db_connect()
Session = sessionmaker(bind=engine)

def main():

    session = Session()
    apartments = session.query(ApartmentModel)

    distances = []
    ratios = []

    for apartment in apartments:

        pos = apartment.gps
        if pos is None: continue
        pos = eval(pos)
        distance = location.get_distance(pos)

        rent = apartment.rent
        livingspace = apartment.livingspace
        if livingspace is None: continue
        if rent is None: continue
        ratio = rent / livingspace

        distances.append(distance)
        ratios.append(ratio)


    print(distances)
    print(ratios)

    plt.plot(distances, ratios, 'k.')
    plt.ylim([0, 30])
    plt.savefig("fig_ratio_overview")


    return

if __name__ == '__main__':
    main()
