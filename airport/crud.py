from fastapi import HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    joinedload,
)

from airport import schemas
from airport.models import Airport, Route


async def generator_id(db: AsyncSession, model):
    existing_ids_query = select(model.id)
    existing_ids = await db.execute(existing_ids_query)
    existing_ids_set = set(row[0] for row in existing_ids)

    new_id = 1
    while new_id in existing_ids_set:
        new_id += 1
    return new_id


async def get_object_or_none(db: AsyncSession, model, **kwargs):
    query = select(model).filter_by(**kwargs)
    result = await db.execute(query)
    return result.scalar()


async def get_all_airports(db: AsyncSession):
    query = select(Airport)
    airport_list = await db.execute(query)
    return [airport for airport in airport_list.scalars()]


async def get_airport_by_airport_code(db: AsyncSession, airport_code: str):
    query = select(Airport).where(Airport.airport_code == airport_code)
    res = await db.execute(query)
    user_row = res.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=404,
            detail=f"The airport with airport code {airport_code} does not exist",
        )
    if user_row is not None:
        return user_row[0]


async def create_airport(db: AsyncSession, airport_data: schemas.AirportCreate):
    query = select(Airport).where(Airport.airport_code == airport_data.airport_code)
    airport = await db.execute(query)

    if airport.scalar():
        raise HTTPException(
            status_code=409,
            detail=f"The airport with code {airport_data.airport_code} already exist",
        )
    query = (
        insert(Airport)
        .values(
            airport_code=airport_data.airport_code,
            name=airport_data.name,
            closets_big_city=airport_data.closets_big_city,
        )
        .returning(Airport.airport_code)
    )
    result = await db.execute(query)
    await db.commit()
    airport_code = result.scalars().first()
    response = {**airport_data.model_dump(), "airport_code": airport_code}
    return response


async def update_airport(
        db: AsyncSession, airport_data: schemas.AirportBase, airport_code: str
):
    db_airport = await get_airport_by_airport_code(db, airport_code=airport_code)
    for attr, value in airport_data.dict().items():
        setattr(db_airport, attr, value)

    await db.commit()
    await db.refresh(db_airport)
    return db_airport


async def delete_airport(db: AsyncSession, airport_code: str):
    db_airport = await get_airport_by_airport_code(db, airport_code=airport_code)
    await db.delete(db_airport)
    await db.commit()
    return HTTPException(
        status_code=200, detail=f"Airport with code №{airport_code} has been deleted."
    )


async def get_all_routes(
        db: AsyncSession, source_airport_code: str, destination_airport_code: str
):
    query = select(Route).options(
        joinedload(Route.source), joinedload(Route.destination)
    )
    if source_airport_code:
        query = query.where(Route.source_airport_code == source_airport_code)
    if destination_airport_code:
        query = query.where(Route.destination_airport_code == destination_airport_code)
    route_list = await db.execute(query)

    result = [
        {
            "id": route.id,
            "distance": route.distance,
            "source": route.source.name,
            "destination": route.destination.name,
        }
        for route in route_list.scalars()
    ]

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"There are no routes with your parameters",
        )
    return result


async def create_route(db: AsyncSession, route_data: schemas.RouteCreate):
    new_id = await generator_id(db=db, model=Route)

    source_airport_code = route_data.source_airport_code
    destination_airport_code = route_data.destination_airport_code

    route = await get_object_or_none(
        db,
        model=Route,
        source_airport_code=source_airport_code,
        destination_airport_code=destination_airport_code,
    )
    if route is not None:
        raise HTTPException(status_code=409, detail="Route already exist")
    else:
        query = (
            insert(Route)
            .values(
                id=new_id,
                distance=route_data.distance,
                source_airport_code=route_data.source_airport_code,
                destination_airport_code=route_data.destination_airport_code,
            )
            .returning(Route.id)
        )
        result = await db.execute(query)

        created_route = result.scalar()
        await db.commit()
        response = {**route_data.model_dump(), "id": created_route}
        return response


async def get_route_by_id(db: AsyncSession, route_id: int):
    query = (
        select(Route)
        .options(joinedload(Route.source), joinedload(Route.destination))
        .where(Route.id == route_id)
    )
    res = await db.execute(query)
    route = res.scalar()

    if not route:
        raise HTTPException(
            status_code=404,
            detail=f"The route with id#{route_id} does not exist",
        )
    return route


async def update_route(
        db: AsyncSession, route_data: schemas.RouteCreate, route_id: int
):
    query = select(Route).where(Route.id == route_id)
    db_route = await db.execute(query)
    route = db_route.scalar()
    for attr, value in route_data.dict().items():
        setattr(route, attr, value)

    await db.commit()
    await db.refresh(route)
    return route


async def delete_route(db: AsyncSession, route_id: int):
    db_route = await get_route_by_id(db, route_id=route_id)
    await db.delete(db_route)
    await db.commit()
    return HTTPException(
        status_code=204, detail=f"Route with id №{route_id} has been deleted."
    )
