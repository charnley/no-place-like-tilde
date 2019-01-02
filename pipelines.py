
from sqlalchemy.orm import sessionmaker

import requests
import os

import json
import models

import wingo_fiber

def save_appendix(model, item):

    idx = model.id

    # Init
    directory = "results/{:}".format(idx)
    if not os.path.exists(directory):
        os.mkdir(directory)

    # Download images
    for i, url in enumerate(item['images']):
        response = requests.get(url, stream=True)
        ext = url.split(".")[-1]

        with open(directory + '/img_{:}.{:}'.format(i, ext), 'wb') as f:
            f.write(response.content)

        del response

    # Download appendix
    for i, url in enumerate(item['appendix']):

        ext = url.split(".")[-1]
        if ext is not "pdf":
            continue

        response = requests.get(url, stream=True)

        with open(directory + '/app_{:}.{:}'.format(i, ext), 'wb') as f:
            f.write(response.content)

        del response

    return


class ApartmentPipeline(object):

    def __init__(self):

        engine = models.db_connect()
        models.create_table(engine)
        self.Session = sessionmaker(bind=engine)


    def process_item(self, item, spider):
        """

        This method is called for every returned item

        """

        session = self.Session()

        # is this a new apartment
        exists = session.query(models.ApartmentModel).filter_by(url=item['url']).count() > 0
        if exists:
            return item

        # convert from ApartmentItem to ApartmentModel
        model = models.ApartmentModel()
        model.url = item['url']
        model.address = item['address']
        model.rent = item['rent']
        model.rooms = item['rooms']
        model.livingspace = item['livingspace']

        try:
            session.add(model)
            session.commit()

            print(model)

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item

