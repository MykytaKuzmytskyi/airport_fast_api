from typing import List

from pydantic import BaseModel


class TicketCreateSchema(BaseModel):
    row: int
    seat: int
    flight: int

    class ConfigDict:
        from_attributes = True


class OrderCreateSchema(BaseModel):
    tickets: List[TicketCreateSchema]

    class ConfigDict:
        from_attributes = True
