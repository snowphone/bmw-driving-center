from datetime import date
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

    @classmethod
    def _date_with_weekday(cls, dt: str):
        it = date.fromisoformat(dt)
        return it.strftime("%Y-%m-%d (%a)")

    def prettify_date(self):
        return self.copy(update={"date": self._date_with_weekday(self.date)})


ReturnType = Dict[str, list[ProgramInDate]]


def prettify_date(obj: ReturnType):
    return {k: [it.prettify_date() for it in v] for k, v in obj.items()}
