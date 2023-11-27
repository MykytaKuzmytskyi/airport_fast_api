from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from dependencies import get_db
from flight import schemas, crud
from user import auth
from user.models import User

router = APIRouter()


@router.get("/crews", response_model=list[schemas.CrewBase], tags=["Crew"])
async def read_crews(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth.current_superuser),
):
    routes = await crud.get_all_crews(db=db)
    return routes


@router.post(
    "/crew",
    tags=["Crew"],
    status_code=status.HTTP_201_CREATED,
)
async def crews_create(
        db: AsyncSession = Depends(get_db),
        crew_data: schemas.CrewCreate | None = None,
        user: User = Depends(auth.current_superuser),
):
    return await crud.create_crew(db=db, crew_data=crew_data)


@router.delete(
    "/crew/{crew_id}",
    tags=["Crew"],
)
async def delete_route(
        db: AsyncSession = Depends(get_db),
        crew_id: int = None,
        user: User = Depends(auth.current_superuser),
):
    return await crud.delete_crew(db=db, crew_id=crew_id)


@router.get(
    "/flights",
    tags=["Flight"],
)
async def read_flights(
        db: AsyncSession = Depends(get_db),
        # user: User = Depends(auth.current_user),
):
    return await crud.get_all_flights(db=db)


@router.get(
    "/flights/{flight_id}",
    tags=["Flight"],
    response_model=schemas.FlightDetail
)
async def read_flight(db: AsyncSession = Depends(get_db), flight_id: int = None):
    return await crud.get_flight_by_id(db=db, flight_id=flight_id)


@router.post(
    "/flight",
    tags=["Flight"],
    status_code=status.HTTP_201_CREATED,
)
async def flights_create(
        db: AsyncSession = Depends(get_db), flight_data: schemas.FlightCreate | None = None
):
    return await crud.create_flight(db=db, flight_data=flight_data)


@router.put(
    "/flight/{flight_id}",
    tags=["Flight"],
    status_code=status.HTTP_200_OK,
)
async def flight_update(
        db: AsyncSession = Depends(get_db),
        flight_id: int = None,
        flight_data: schemas.FlightCreate | None = None,
):
    return await crud.update_flight(db=db, flight_id=flight_id, flight_data=flight_data)


@router.delete(
    "/flight/{flight_id}",
    tags=["Flight"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_flight(
        db: AsyncSession = Depends(get_db),
        flight_id: int = None,
):
    return await crud.delete_flight(db=db, flight_id=flight_id)
