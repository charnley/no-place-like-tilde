
from sqlalchemy.orm import sessionmaker
import models

engine = models.db_connect()
models.create_table(engine)
Session = sessionmaker(bind=engine)

session = Session()
item_test = models.ApartmentModel()
item_test.rent = 1600
item_test.index = 3453453453
item_test.address = "Degnestavnen 15, 2400 København NV"
item_test.livingspace = 80

try:
    session.add(item_test)
    session.commit()

    #test query
    obj = session \
        .query(models.ApartmentModel) \
        .order_by(models.ApartmentModel.id.desc()) \
        .first()

    print(obj)

except:
    session.rollback()
    raise

finally:
    session.close()

