from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from airport import schemas, crud

from dependencies import get_db
from user import auth

from user.models import User

router = APIRouter()


def parameters(
        airport_code: str | None = None,
        db: AsyncSession = Depends(get_db),
        airport_data: schemas.Airport | schemas.AirportCreate | None = None,
):
    return {
        "db": db,
        "airport_code": airport_code,
        "airport_data": airport_data,
    }


CommonsDep = Annotated[dict, Depends(parameters)]


@router.get("/airports", response_model=list[schemas.Airport], tags=["Airport"])
async def read_airports(
        parameter: CommonsDep,
):
    return await crud.get_all_airports(db=parameter["db"])


@router.post(
    "/airports",
    response_model=schemas.Airport,
    tags=["Airport"],
    status_code=status.HTTP_201_CREATED,
)
async def airport_create(
        parameter: CommonsDep, user: User = Depends(auth.current_superuser)
):
    return await crud.create_airport(
        db=parameter["db"], airport_data=parameter["airport_data"]
    )


@router.get(
    "/airports/{airport_code}", response_model=schemas.Airport, tags=["Airport"]
)
async def read_airport(parameter: CommonsDep):
    return await crud.get_airport_by_airport_code(
        db=parameter["db"], airport_code=parameter["airport_code"]
    )


@router.put(
    "/airports/{airport_code}", response_model=schemas.Airport, tags=["Airport"]
)
async def update_airport(
        parameter: CommonsDep, user: User = Depends(auth.current_superuser)
):
    return await crud.update_airport(
        db=parameter["db"],
        airport_data=parameter["airport_data"],
        airport_code=parameter["airport_code"],
    )


@router.delete(
    "/airports/{airport_code}", tags=["Airport"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_airport(
        parameter: CommonsDep,
        user: User = Depends(auth.current_superuser),
):
    return await crud.delete_airport(
        db=parameter["db"], airport_code=parameter["airport_code"]
    )


@router.get("/routes", response_model=list[schemas.RouteList], tags=["Routes"])
async def read_routes(
        db: AsyncSession = Depends(get_db),
        source_airport_code: str = None,
        destination_airport_code: str = None,
):
    return await crud.get_all_routes(
        db=db,
        source_airport_code=source_airport_code,
        destination_airport_code=destination_airport_code,
    )


@router.get("/route/{route_id}", response_model=schemas.Route, tags=["Routes"])
async def read_route(
        db: AsyncSession = Depends(get_db),
        route_id: int = None,
):
    route = await crud.get_route_by_id(db=db, route_id=route_id)
    result_route = {
        "id": route.id,
        "distance": route.distance,
        "source": route.source,
        "destination": route.destination,
    }
    return result_route


@router.post(
    "/route",
    tags=["Routes"],
    response_model=schemas.RouteCreate,
    status_code=status.HTTP_201_CREATED,
)
async def route_create(
        db: AsyncSession = Depends(get_db),
        route_data: schemas.RouteCreate | None = None,
        user: User = Depends(auth.current_superuser),
):
    return await crud.create_route(db=db, route_data=route_data)


@router.put(
    "/route/{route_id}",
    tags=["Routes"],
)
async def update_route(
        db: AsyncSession = Depends(get_db),
        route_id: int = None,
        route_data: schemas.RouteCreate = None,
        user: User = Depends(auth.current_superuser),
):
    return await crud.update_route(db=db, route_id=route_id, route_data=route_data)


@router.delete(
    "/route/{route_id}",
    tags=["Routes"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route(
        db: AsyncSession = Depends(get_db),
        route_id: int = None,
        user: User = Depends(auth.current_superuser),
):
    return await crud.delete_route(db=db, route_id=route_id)
