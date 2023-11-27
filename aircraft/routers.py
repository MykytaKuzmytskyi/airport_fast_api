from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from aircraft import schemas, crud
from aircraft.schemas import AircraftType, AircraftTypeCreate, AircraftCreate
from dependencies import get_db
from user import auth
from user.models import User

router = APIRouter()


def parameters(
    db: AsyncSession = Depends(get_db),
    aircraft_code: str | None = None,
    aircraft_data: AircraftCreate | None = None,
):
    return {
        "db": db,
        "aircraft_code": aircraft_code,
        "aircraft_data": aircraft_data,
    }


CommonsDep = Annotated[dict, Depends(parameters)]


@router.get("/aircraft_types", response_model=list[AircraftType], tags=["Aircraft"])
async def read_airplane_types(
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_all_aircraft_type(db=db)


@router.post(
    "/aircraft_type",
    response_model=schemas.AircraftTypeCreate,
    tags=["Aircraft"],
    status_code=status.HTTP_201_CREATED,
)
async def aircraft_type_create(
    db: AsyncSession = Depends(get_db),
    aircraft_type_data: AircraftTypeCreate = None,
    user: User = Depends(auth.current_superuser),
):
    return await crud.create_aircraft_type(
        db=db, aircraft_type_data=aircraft_type_data
    )


@router.get(
    "/aircraft_type/{wtc}", response_model=schemas.AircraftType, tags=["Aircraft"]
)
async def read_aircraft_type_by_wtc(
    db: AsyncSession = Depends(get_db),
    wtc: str = None,
):
    return await crud.get_aircraft_type_by_wtc(db=db, wtc=wtc)


@router.put(
    "/aircraft_type/{wtc}",
    tags=["Aircraft"],
)
async def update_aircraft_type(
    db: AsyncSession = Depends(get_db),
    wtc: str = None,
    aircraft_type_data: AircraftTypeCreate = None,
    user: User = Depends(auth.current_superuser),
):
    return await crud.update_aircraft_type(
        db=db, wtc=wtc, aircraft_type_data=aircraft_type_data
    )


@router.delete(
    "/aircraft_type/{wtc}",
    tags=["Aircraft"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_aircraft_type(
    db: AsyncSession = Depends(get_db),
    wtc: str = None,
    user: User = Depends(auth.current_superuser),
):
    return await crud.delete_aircraft_type(db=db, wtc=wtc)


@router.get("/aircrafts", tags=["Aircraft"])
async def read_aircrafts(
    parameter: CommonsDep,
):
    return await crud.get_all_aircrafts(db=parameter["db"])


@router.get("/aircraft/{aircraft_code}", tags=["Aircraft"])
async def read_aircraft_by_code(parameter: CommonsDep):
    return await crud.get_aircraft_by_aircraft_code(
        db=parameter["db"], aircraft_code=parameter["aircraft_code"]
    )


@router.post(
    "/aircraft",
    response_model=schemas.AircraftCreate,
    tags=["Aircraft"],
    status_code=status.HTTP_201_CREATED,
)
async def aircraft_create(
    parameter: CommonsDep, user: User = Depends(auth.current_superuser)
):
    return await crud.create_aircraft(
        db=parameter["db"], aircraft_data=parameter["aircraft_data"]
    )


@router.put(
    "/aircraft/{aircraft_code}",
    response_model=schemas.AircraftCreate,
    tags=["Aircraft"],
)
async def update_airport(
    parameter: CommonsDep, user: User = Depends(auth.current_superuser)
):
    return await crud.update_airport(
        db=parameter["db"],
        aircraft_data=parameter["aircraft_data"],
        aircraft_code=parameter["aircraft_code"],
    )


@router.delete(
    "/aircraft/{aircraft_code}",
    tags=["Aircraft"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_airport(
    parameter: CommonsDep, user: User = Depends(auth.current_superuser)
):
    return await crud.delete_aircraft(
        db=parameter["db"], aircraft_code=parameter["aircraft_code"]
    )
