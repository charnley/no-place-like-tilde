
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
    sqm = []

    for apartment in apartments:

        pos = apartment.gps
        if pos is None: continue
        pos = eval(pos)
        distance = location.get_distance(pos)

        rent = apartment.rent
        livingspace = apartment.livingspace
        if livingspace is None: continue
        if livingspace < 10: continue
        if rent is None: continue
        ratio = rent / livingspace

        if ratio > 75: continue

        distances.append(distance)
        ratios.append(ratio)
        sqm.append(livingspace)


    # print(distances)
    # print(ratios)


    fig, ax = plt.subplots(1, 1, figsize=(5, 5))

    ax.plot(sqm, ratios, 'k.')

    ax.set_xlabel('Livingspace [m2]', fontweight='medium', fontsize=13)
    ax.set_ylabel('Ratio [chf/m2]', fontweight='medium', fontsize=13)


    handles, labels = ax.get_legend_handles_labels()
    handles = [h[0] for h in handles]
    # ax.legend(handles, labels, loc='upper right', frameon=False, numpoints=1)

    ax.yaxis.grid(True, zorder=0)
    ax.xaxis.grid(True, zorder=0)

    filename = "fig_ratio_overview"

    plt.savefig(filename + ".png", bbox_inches="tight")
    plt.savefig(filename + ".pdf", bbox_inches="tight")



    return

if __name__ == '__main__':
    main()
