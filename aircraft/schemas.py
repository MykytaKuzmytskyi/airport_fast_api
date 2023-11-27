from pydantic import BaseModel


class AircraftType(BaseModel):
    name: str


class AircraftTypeCreate(AircraftType):
    wtc: str
    name: str


class AircraftBase(BaseModel):
    aircraft_code: str
    model: str
    range: int
    rows: int
    seats_in_row: int


class Aircraft(AircraftBase):
    aircraft_type: str

    class ConfigDict:
        from_attributes = True
        orm_mode = True


class AircraftCreate(AircraftBase):
    aircraft_type_wtc: str

    class ConfigDict:
        from_attributes = True
