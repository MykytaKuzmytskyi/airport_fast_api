from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base
from user.models import User


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    user_id = Column(Integer, ForeignKey("user.id"))

    users = relationship(User, back_populates="orders")
    tickets = relationship("Ticket", back_populates="orders")


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True, index=True)
    row = Column(Integer)
    seat = Column(Integer)

    flight_id = Column(Integer, ForeignKey("flight.id"))
    order_id = Column(Integer, ForeignKey("order.id"))

    flights = relationship("Flight", back_populates="tickets")
    orders = relationship("Order", back_populates="tickets")

    __table_args__ = (
        UniqueConstraint("row", "seat", "flight_id", name="unique_ticket"),
    )
