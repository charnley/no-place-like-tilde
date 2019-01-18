
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


    for chf in [1000, 1500, 2000]:
        livingspaces = range(10, 200)
        livingspaces = list(livingspaces)
        chf_ratios = []
        for livingspace in livingspaces:
            ratio = chf / livingspace
            chf_ratios.append(ratio)
        ax.plot(livingspaces, chf_ratios, label=str(chf) + " chf")


    leg = ax.legend(loc="best", borderaxespad=0.1, framealpha=1.0, fancybox=False, borderpad=1)
    leg.get_frame().set_linewidth(0.0)
    leg.get_frame().set_facecolor('#ffffff')

    ax.yaxis.grid(True, zorder=0)
    ax.xaxis.grid(True, zorder=0)

    ax.set_xlim((0, 200))
    ax.set_ylim((10, 40))

    filename = "fig_ratio_overview"

    plt.savefig(filename + ".png", bbox_inches="tight")
    plt.savefig(filename + ".pdf", bbox_inches="tight")



    return

if __name__ == '__main__':
    main()
