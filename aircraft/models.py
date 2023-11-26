from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base
from flight.models import Flight


class AircraftType(Base):
    __tablename__ = "aircraft_type"

    wtc = Column(
        String(1), primary_key=True, index=True, comment="Wake Turbulence Categories"
    )
    name = Column(String(255), unique=True)

    aircraft = relationship("Aircraft", back_populates="aircraft_types")


class Aircraft(Base):
    __tablename__ = "aircraft"

    aircraft_code = Column(String(10), primary_key=True, index=True)
    model = Column(String(255), unique=True)
    range = Column(Integer)
    rows = Column(Integer)
    seats_in_row = Column(Integer)
    aircraft_type_wtc = Column(String(1), ForeignKey("aircraft_type.wtc"))

    aircraft_types = relationship(AircraftType, back_populates="aircraft")
    flights = relationship(Flight, back_populates="aircraft")
