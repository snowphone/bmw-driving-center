from typing import (
    Dict,
    TypedDict,
)


class ProgramTime(TypedDict):
    turnSequence: str
    turnStartTime: str
    turnEndTime: str
    turnClassificationTotalProductQuantity: int
    turnClassificationRemainingProductQuantity: int


class ProgramInDate(TypedDict):
    date: str
    programs: list[ProgramTime]


ReturnType = Dict[str, list[ProgramInDate]]
