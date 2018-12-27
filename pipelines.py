
from sqlalchemy.orm import sessionmaker

import json
import models

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



class ApartmentJsonPipeline(object):

    def open_spider(self, spider):
        self.file = open('item.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

