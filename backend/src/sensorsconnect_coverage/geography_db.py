# geography_db.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create an engine and a base class
engine = create_engine('sqlite:///sensorsconnect_coverage/geography.db', echo=False)
Base = declarative_base()

# Define the Country model
class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cities = relationship('City', back_populates='country', cascade='all, delete-orphan')

# Define the City model
class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    country = relationship('Country', back_populates='cities')

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Function to add a country
def add_country(name):
    country = Country(name=name)
    session.add(country)
    session.commit()

# Function to add a city
def add_city(name, country_name):
    country = session.query(Country).filter_by(name=country_name).first()
    if country:
        city = City(name=name, country=country)
        session.add(city)
        session.commit()
    else:
        print(f"Country '{country_name}' does not exist. Please add it first.")

# Function to check if a city-country pair exists
def check_city_country_exists(city_name, country_name):
    city = (
        session.query(City)
        .join(Country)
        .filter(City.name == city_name, Country.name == country_name)
        .first()
    )
    return city is not None

# Function to close the session
def close_session():
    session.close()
