from fastapi import HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    joinedload,
    selectinload,
)
from sqlalchemy.future import select as sel
from aircraft.models import Aircraft
from airport.crud import generator_id
from flight import schemas
from flight.models import Crew, Flight, flight_crew
from order.models import Ticket


async def get_all_crews(db: AsyncSession):
    query = select(Crew)
    crew_list = await db.execute(query)
    return [crew for crew in crew_list.scalars()]


async def get_crew_by_id(db: AsyncSession, crew_id: int):
    query = select(Crew).where(Crew.id == crew_id)
    res = await db.execute(query)
    crew = res.scalar()
    if not crew:
        raise HTTPException(
            status_code=404,
            detail=f"The crew with id #{crew_id} does not exist",
        )
    return crew


async def create_crew(db: AsyncSession, crew_data: schemas.CrewCreate):
    new_id = await generator_id(db=db, model=Crew)
    try:
        query = (
            insert(Crew)
            .values(
                id=new_id,
                first_name=crew_data.first_name,
                last_name=crew_data.last_name,
            )
            .returning(Crew.id)
        )
        result = await db.execute(query)
        await db.commit()
        crew_id = result.scalars().first()
        response = {**crew_data.model_dump(), "id": crew_id}
        return response
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Duplicate entry: Crew with the same first_name and last_name already exists."
        )


async def delete_crew(db: AsyncSession, crew_id: int):
    db_crew = await get_crew_by_id(db=db, crew_id=crew_id)
    await db.delete(db_crew)
    await db.commit()
    headers = {"X-Info": f"Crew with id #{crew_id} has been deleted."}
    return Response(
        content=None,
        headers=headers,
        status_code=status.HTTP_204_NO_CONTENT,
    )


async def get_all_flights(db: AsyncSession, order_by_field: str = "departure_time"):
    query = (
        select(
            Flight,
            (Aircraft.rows * Aircraft.seats_in_row - func.count(Ticket.id)).label("tickets_available"),
        )
        .join(Aircraft, Flight.aircraft_code == Aircraft.aircraft_code)
        .join(Ticket, Flight.id == Ticket.flight_id, isouter=True)
        .options(joinedload(Flight.crews), joinedload(Flight.aircraft))
        .group_by(Flight.id, Aircraft.rows, Aircraft.seats_in_row)
    ).order_by(getattr(Flight, order_by_field))
    flights = await db.execute(query)

    result = [
        {
            "id": flight.id,
            "route_id": flight.route_id,
            "aircraft": flight.aircraft.model,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "tickets_available": tickets_available,
            "crews": flight.crews,
        }
        for flight, tickets_available in flights.unique()
    ]
    return result


async def get_flight_by_id(db: AsyncSession, flight_id: int):
    query = (
        select(Flight).options(joinedload(Flight.crews), selectinload(Flight.aircraft)).where(Flight.id == flight_id)
    )
    res = await db.execute(query)
    flight = res.scalar()
    if not flight:
        raise HTTPException(
            status_code=404,
            detail=f"The flight with id#{flight_id} does not exist",
        )
    result = {
        "id": flight.id,
        "route_id": flight.route_id,
        "aircraft": flight.aircraft.model,
        "departure_time": flight.departure_time,
        "arrival_time": flight.arrival_time,
        "crews": flight.crews,
    }
    return result


async def create_flight(db: AsyncSession, flight_data: schemas.FlightCreate):
    new_id = await generator_id(db=db, model=Flight)

    crew_values = [
        {"flight_id": new_id, "crew_id": crew_id} for crew_id in flight_data.crews
    ]

    query = (
        insert(Flight)
        .values(
            id=new_id,
            route_id=flight_data.route_id,
            aircraft_code=flight_data.aircraft_code,
            departure_time=flight_data.departure_time,
            arrival_time=flight_data.arrival_time,
        )
        .returning(Flight.id)
    )
    result = await db.execute(query)
    await db.commit()
    flight_id = result.scalars().first()

    await db.execute(flight_crew.insert().values(crew_values))
    await db.commit()

    response = {**flight_data.dict(), "id": flight_id}
    return response


async def update_flight(
        db: AsyncSession, flight_data: schemas.FlightBase, flight_id: int
):
    db_flight = await get_flight_by_id(db, flight_id=flight_id)

    new_crew_ids = flight_data.crews
    db_flight.crews.clear()

    for crew_id in new_crew_ids:
        crew = await get_crew_by_id(db, crew_id=crew_id)
        db_flight.crews.append(crew)

    # Update other attributes
    for attr, value in flight_data.dict().items():
        if attr != "crews":
            setattr(db_flight, attr, value)

    await db.commit()
    await db.refresh(db_flight)
    return db_flight


async def delete_flight(db: AsyncSession, flight_id: int):
    db_flight = await get_flight_by_id(db, flight_id=flight_id)
    await db.delete(db_flight)
    await db.commit()
    return HTTPException(
        status_code=200, detail=f"Flight with id №{flight_id} has been deleted."
    )
