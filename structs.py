from typing import Dict

from pydantic import BaseModel


class ProgramTime(BaseModel):
    turnSequence: str
    turnStartTime: str
    turnEndTime: str
    turnClassificationTotalProductQuantity: int
    turnClassificationRemainingProductQuantity: int


class ProgramInDate(BaseModel):
    date: str
    programs: list[ProgramTime]


ReturnType = Dict[str, list[ProgramInDate]]
