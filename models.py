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
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True)
    data_initial = Column('data_start', Date())
    data_removed = Column('data_end', Date())

    internet = Column('internet', String())

    address = Column('address', String())
    gps = Column('gps', String())

    rent = Column('rent', Float())

    livingspace = Column('squaremeter', Float())
    rooms = Column('rooms', Float())

    apartment_type = Column('apartment_type', String())
    floor = Column('floor', Float())

    available = Column('avaliable', String())

    url = Column('url', String())
    description = Column('description', String())

    def __repr__(self):

        return "<Apartment {:} {:} m2 / {:} chf - {:}>".format(
            self.id,
            self.livingspace,
            self.rent,
            self.address)

