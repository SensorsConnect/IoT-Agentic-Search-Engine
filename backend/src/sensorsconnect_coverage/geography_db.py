# geography_db.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.engine import Base, engine, SessionLocal

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

# Function to add a country
def add_country(name):
    session = SessionLocal()
    try:
        country = Country(name=name)
        session.add(country)
        session.commit()
    finally:
        session.close()

# Function to add a city
def add_city(name, country_name):
    session = SessionLocal()
    try:
        country = session.query(Country).filter_by(name=country_name).first()
        if country:
            city = City(name=name, country=country)
            session.add(city)
            session.commit()
        else:
            print(f"Country '{country_name}' does not exist. Please add it first.")
    finally:
        session.close()

# Function to check if a city-country pair exists
def check_city_country_exists(city_name, country_name):
    # A fresh, short-lived session per call avoids a single dropped connection
    # (e.g. "SSL connection has been closed unexpectedly") poisoning every
    # future request with a PendingRollbackError, since a module-level session
    # would never get rolled back or replaced.
    session = SessionLocal()
    try:
        city = (
            session.query(City)
            .join(Country)
            .filter(City.name == city_name, Country.name == country_name)
            .first()
        )
        return city is not None
    finally:
        session.close()

# Kept for backwards-compatible import in sensorsconnect_coverage/test.py; no-op
# now that sessions are opened and closed per call.
def close_session():
    pass
