from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base

flight_crew = Table(
    "flight_crew",
    Base.metadata,
    Column("flight_id", Integer, ForeignKey("flight.id")),
    Column("crew_id", Integer, ForeignKey("crew.id")),
)


class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))

    flights = relationship("Flight", secondary=flight_crew, back_populates="crews")
    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            name="unique_crew_first_name_last_name"
        ),
    )


class Flight(Base):
    __tablename__ = "flight"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    route_id = Column(Integer, ForeignKey("route.id"))
    aircraft_code = Column(
        String(10), ForeignKey("aircraft.aircraft_code"), primary_key=True
    )
    departure_time = Column(TIMESTAMP(timezone=True), nullable=False)
    arrival_time = Column(TIMESTAMP(timezone=True), nullable=False)

    crews = relationship("Crew", secondary=flight_crew, back_populates="flights")
    aircraft = relationship(
        "Aircraft",
        back_populates="flights",
        foreign_keys=aircraft_code,
        primaryjoin="Flight.aircraft_code == Aircraft.aircraft_code",
    )
    tickets = relationship("Ticket", back_populates="flights")
    route = relationship(
        "Route",
        back_populates="flights",
        primaryjoin="Flight.route_id == Route.id",
    )
