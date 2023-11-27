from fastapi import Response, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from aircraft import schemas
from aircraft.models import AircraftType, Aircraft


async def get_all_aircraft_type(db: AsyncSession):
    query = select(AircraftType)
    aircraft_type_list = await db.execute(query)
    return [aircraft_type for aircraft_type in aircraft_type_list.scalars()]


async def create_aircraft_type(
    db: AsyncSession, aircraft_type_data: schemas.AircraftTypeCreate
):
    query = select(AircraftType).where(AircraftType.wtc == aircraft_type_data.wtc)
    aircraft_type = await db.execute(query)

    if aircraft_type.scalar():
        raise HTTPException(
            status_code=409,
            detail=f"The aircraft_type_data with wtc {aircraft_type_data.wtc} already exist",
        )
    query = (
        insert(AircraftType)
        .values(
            wtc=aircraft_type_data.wtc,
            name=aircraft_type_data.name,
        )
        .returning(AircraftType.wtc)
    )
    result = await db.execute(query)
    await db.commit()
    wtc = result.scalars().first()
    response = {**aircraft_type_data.model_dump(), "wtc": wtc}
    return response


async def get_aircraft_type_by_wtc(db: AsyncSession, wtc: str):
    query = select(AircraftType).where(AircraftType.wtc == wtc)
    res = await db.execute(query)
    aircraft_type = res.scalar()
    if not aircraft_type:
        raise HTTPException(
            status_code=404,
            detail=f"The aircraft type with wtc '{wtc}' does not exist",
        )
    else:
        return aircraft_type


async def update_aircraft_type(
    db: AsyncSession, aircraft_type_data: schemas.AircraftTypeCreate, wtc: str
):
    db_aircraft_type = await get_aircraft_type_by_wtc(db, wtc=wtc)
    for attr, value in aircraft_type_data.dict().items():
        setattr(db_aircraft_type, attr, value)

    await db.commit()
    await db.refresh(db_aircraft_type)
    return db_aircraft_type


async def delete_aircraft_type(db: AsyncSession, wtc: str):
    db_aircraft_type = await get_aircraft_type_by_wtc(db, wtc=wtc)
    await db.delete(db_aircraft_type)
    await db.commit()
    headers = {"X-Info": f"Aircraft type with wtc #{wtc} has been deleted."}
    return Response(
        content=None,
        headers=headers,
        status_code=status.HTTP_204_NO_CONTENT,
    )


async def get_all_aircrafts(db: AsyncSession):
    query = select(Aircraft).options(selectinload(Aircraft.aircraft_types))
    aircraft_list = await db.execute(query)
    return [
        dict(
            model=aircraft.model,
            aircraft_code=aircraft.aircraft_code,
            rows=aircraft.rows,
            seats_in_row=aircraft.seats_in_row,
            range=aircraft.range,
            aircraft_type=aircraft.aircraft_types.name,
        )
        for aircraft in aircraft_list.scalars()
    ]


async def get_aircraft_by_aircraft_code(db: AsyncSession, aircraft_code: str):
    query = select(Aircraft).where(Aircraft.aircraft_code == aircraft_code)
    res = await db.execute(query)
    user = res.scalar()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"The aircraft with code {aircraft_code} does not exist",
        )
    return user


async def create_aircraft(db: AsyncSession, aircraft_data: schemas.AircraftCreate):
    query = select(Aircraft).where(
        Aircraft.aircraft_code == aircraft_data.aircraft_code
    )
    aircraft = await db.execute(query)

    if aircraft.scalar():
        raise HTTPException(
            status_code=409,
            detail=f"The aircraft with code {aircraft_data.aircraft_code} already exist",
        )

    query = (
        insert(Aircraft)
        .values(
            aircraft_code=aircraft_data.aircraft_code,
            model=aircraft_data.model,
            range=aircraft_data.range,
            rows=aircraft_data.rows,
            seats_in_row=aircraft_data.seats_in_row,
            aircraft_type_wtc=aircraft_data.aircraft_type_wtc,
        )
        .returning(Aircraft.aircraft_code)
    )
    result = await db.execute(query)
    await db.commit()
    aircraft_code = result.scalars().first()
    response = {**aircraft_data.model_dump(), "aircraft_code": aircraft_code}
    return response


async def update_airport(
    db: AsyncSession, aircraft_data: schemas.AircraftCreate, aircraft_code: str
):
    db_aircraft = await get_aircraft_by_aircraft_code(db, aircraft_code=aircraft_code)
    for attr, value in aircraft_data.dict().items():
        setattr(db_aircraft, attr, value)

    await db.commit()
    await db.refresh(db_aircraft)
    return db_aircraft


async def delete_aircraft(db: AsyncSession, aircraft_code: str):
    db_aircraft = await get_aircraft_by_aircraft_code(db, aircraft_code=aircraft_code)
    await db.delete(db_aircraft)
    await db.commit()
    headers = {"X-Info": f"Aircraft with code #{aircraft_code} has been deleted."}
    return Response(
        content=None,
        headers=headers,
        status_code=status.HTTP_204_NO_CONTENT,
    )
