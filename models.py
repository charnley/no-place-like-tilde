from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer,
    SmallInteger,
    String,
    Date,
    DateTime,
    Float,
    Boolean,
    Text,
    LargeBinary)

from scrapy.utils.project import get_project_settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """

    connect_string = "sqlite:///database.db"

    return create_engine(connect_string)

def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class ApartmentModel(DeclarativeBase):
    __tablename__ = "apartment_table"

    id = Column(Integer, primary_key=True)

    index = Column('index', Integer)
    address = Column('address', String())
    rent = Column('rent', Float())
    livingspace = Column('squaremeter', Float()) # in m**2

    # images = scrapy.Field()
    # appendix = scrapy.Field()

    # title = scrapy.Field()
    # description = scrapy.Field()

    feature_type = Column('apartment_type', String())
    feature_rooms = Column('rooms', String())
    feature_floor = Column('floor', String())
    feature_available = Column('avaliable', String())

    def __repr__(self):

        return "<Apartment {:} m**2 / {:} chf - {:}>".format(
            self.livingspace,
            self.rent,
            self.address)

