import argparse
from db_settings import *
from sqlalchemy import *
from sqlalchemy.orm import relationship



class Airports(Base):
    __tablename__ = 'airports'
    id = Column(Integer, Sequence('airport_id_seq'), primary_key=True)
    name = Column(String(50), unique=True)
    city = Column(String(50))
    country = Column(String(50))
    iata = Column(CHAR(3))
    icao = Column(CHAR(4))
    latitude = Column(String(50))
    longitude = Column(String(50))
    altitude = Column(String(50))
    timezone = Column(String(50))
    airport_type_enum = Enum('international', 'domestic', name='airport_type_enum')
    type = Column(airport_type_enum)

    def __repr__(self):
        return f"<Airports(name={self.name}, city={self.city}, country={self.country}, iata={self.iata}, icao={self.icao}, type={self.type})>"
    
class Aircrafts(Base):
    __tablename__ = 'aircrafts'
    id = Column(Integer, Sequence('aircraft_id_seq'), primary_key=True)
    model = Column(String(50), unique=True)
    seating_capacity = Column(Integer)
    year_manufactured = Column(Integer)
    
    @validates('year_manufactured')
    def validate_year_manufactured(self, key, value):
        # Perform validation on the year input
        if not (1900 <= value <= 2100):  # You can adjust the range as needed
            raise ValueError("Invalid year of manufacture")
        return value

    def __repr__(self):
        return f"<Aircrafts(model={self.model}, seating_capacity={self.seating_capacity}, year_manufactured={self.year_manufactured})>"

class Routes(Base):
    __tablename__ = 'routes'
    id = Column(Integer, Sequence('route_id_seq'), primary_key=True)
    departure = Column(String(50), ForeignKey('airports.iata'))
    arrival = Column(String(50), ForeignKey('airports.iata'))
    distance = Column(Float)
    duration = Column(Float)

    # Define relationships with the Airports table
    departure_airport = relationship('Airports', foreign_keys=[departure], backref='departures')
    arrival_airport = relationship('Airports', foreign_keys=[arrival], backref='arrivals')

    def __repr__(self):
        return f"<Routes(departure={self.departure}, arrival={self.arrival}, distance={self.distance}, duration={self.duration})>"

class Flights(Base):
    __tablename__ = 'flights'
    id = Column(Integer, Sequence('flight_id_seq'), primary_key=True)
    flight_number = Column(Integer)
    aircraft_id = Column(Integer, ForeignKey('aircrafts.id'))
    route_id = Column(Integer, ForeignKey('routes.id'))
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    status_enum = Enum('ontime', 'delayed', 'cancelled', name='status_enum')
    status = Column(status_enum)
    
    # Define relationships with the Aircrafts and Routes tables
    aircraft = relationship('Aircrafts', backref='flights')
    route = relationship('Routes', backref='flights')
    
    def __repr__(self):
        return f"<Flights(flight_number={self.flight_number}, aircraft_id={self.aircraft_id}, route_id={self.route_id}, departure_time={self.departure_time}, arrival_time={self.arrival_time}, status={self.status})>"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--migrate', action='store_true', default=True)
    args = parser.parse_args()

    # if args.migrate:
    #     migrate()

    # migrate()
    # user = User(username='admin',email = 'admin@gmail.com')
    # session.add(user)
    # # print(session)
    # session.commit()
    # user = session.query(User).first()
    # print(user)