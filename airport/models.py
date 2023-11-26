from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class Airport(Base):
    __tablename__ = "airport"

    airport_code = Column(String(3), primary_key=True, index=True)
    name = Column(String(255), unique=True)
    closets_big_city = Column(String(255))

    sources = relationship(
        "Route", back_populates="source", foreign_keys="Route.source_airport_code"
    )
    destinations = relationship(
        "Route",
        back_populates="destination",
        foreign_keys="Route.destination_airport_code",
    )


class Route(Base):
    __tablename__ = "route"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    distance = Column(Integer)
    source_airport_code = Column(
        String(3), ForeignKey("airport.airport_code"), primary_key=True
    )
    destination_airport_code = Column(
        String(3), ForeignKey("airport.airport_code"), primary_key=True
    )

    source = relationship(
        "Airport",
        back_populates="sources",
        foreign_keys=source_airport_code,
        primaryjoin="Route.source_airport_code == Airport.airport_code",
    )
    destination = relationship(
        "Airport",
        back_populates="destinations",
        foreign_keys=destination_airport_code,
        primaryjoin="Route.destination_airport_code == Airport.airport_code",
    )

    flights = relationship("Flight", back_populates="route")

    __table_args__ = (
        UniqueConstraint(
            "source_airport_code",
            "destination_airport_code",
            name="unique_route_source_destination",
        ),
    )
