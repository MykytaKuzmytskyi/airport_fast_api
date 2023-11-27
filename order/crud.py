from fastapi import HTTPException
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from order import schemas
from flight.crud import get_flight_by_id
from order.models import Order, Ticket


def validate_ticket(row, seat, airplane):
    for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
        (row, "row", "rows"),
        (seat, "seat", "seats_in_row"),
    ]:
        count_attrs = getattr(airplane, airplane_attr_name)
        if not (1 <= ticket_attr_value <= count_attrs):
            raise HTTPException(
                status_code=400,
                detail=f"{ticket_attr_name}: {ticket_attr_name} "
                f"number must be in available range: "
                f"(1, {airplane_attr_name}): "
                f"(1, {count_attrs})",
            )


async def create_order(db: AsyncSession, order_data: schemas.OrderCreateSchema, user):
    async with db.begin() as transaction:
        new_order = Order(user_id=user.id)
        db.add(new_order)
        await db.flush()

        created_tickets = []
        for ticket_data in order_data.tickets:
            flight = await get_flight_by_id(db=db, flight_id=ticket_data.flight)
            aircraft = flight.aircraft
            validate_ticket(ticket_data.row, ticket_data.seat, aircraft)

            try:
                query = insert(Ticket).values(
                    row=ticket_data.row,
                    seat=ticket_data.seat,
                    flight_id=ticket_data.flight,
                    order_id=new_order.id,
                )
                await db.execute(query)
            except IntegrityError as e:
                await transaction.rollback()
                raise HTTPException(status_code=400, detail="Ticket already exists")

            created_tickets.append(
                {
                    "row": ticket_data.row,
                    "seat": ticket_data.seat,
                    "flight": ticket_data.flight,
                }
            )

        response = {
            "order_id": new_order.id,
            "created_at": new_order.created_at,
            "user_id": new_order.user_id,
            "tickets": created_tickets,
        }
        await transaction.commit()
        return response
