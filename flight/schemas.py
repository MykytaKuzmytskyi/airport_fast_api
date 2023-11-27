import datetime
from typing import List

from pydantic import BaseModel


class CrewBase(BaseModel):
    first_name: str
    last_name: str


class CrewCreate(CrewBase):
    pass


class CrewUpdate(CrewBase):
    id: int

    class ConfigDict:
        from_attributes = True


class FlightBase(BaseModel):
    route_id: int
    aircraft_code: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    crews: List[int]


class FlightList(FlightBase):
    id: int
    tickets_available: int


class FlightDetail(BaseModel):
    id: int
    route_id: int
    aircraft: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    crews: List[CrewUpdate]


class FlightCreate(FlightBase):
    pass


class FlightUpdate(FlightBase):
    id: int

    class ConfigDict:
        from_attributes = True
