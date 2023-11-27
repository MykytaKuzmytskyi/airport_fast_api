from pydantic import BaseModel


class AirportBase(BaseModel):
    airport_code: str
    name: str
    closets_big_city: str


class AirportCreate(AirportBase):
    pass


class Airport(AirportBase):
    class ConfigDict:
        from_attributes = True


class RouteBase(BaseModel):
    distance: int
    source_airport_code: str
    destination_airport_code: str


class Route(BaseModel):
    id: int
    distance: int
    source: AirportBase
    destination: AirportBase


class RouteList(BaseModel):
    id: int
    distance: int
    source: str
    destination: str


class RouteCreate(RouteBase):
    pass


class RouteUpdate(RouteBase):
    id: int

    class ConfigDict:
        from_attributes = True
