from __future__ import annotations

import logging
from datetime import (
    date,
    datetime,
    timedelta,
)
from functools import lru_cache

from holidays import SouthKorea

logger = logging.getLogger()


@lru_cache
def holidays_in_korea():
    year = datetime.now().year
    years = frozenset([year, year + 1])
    holiday_set = {"2023-05-29"} | {
        it.isoformat()
        for it in set(SouthKorea(years=years).keys()) | get_all_weekends(years)
    }

    logger.debug(f"Holidays: {holiday_set}")
    return holiday_set


@lru_cache
def get_all_weekends(years: frozenset[int]) -> set[date]:
    weekends = set()

    # Iterate over the years
    for year in years:
        # Iterate over the months
        for month in range(1, 13):
            # Get the first day of the month
            first_day = date(year, month, 1)

            # Find the first Saturday of the month
            first_sat = first_day + timedelta(days=(5 - first_day.weekday() + 7) % 7)

            # Find the first Sunday of the month
            first_sun = first_day + timedelta(days=(6 - first_day.weekday() + 7) % 7)

            # Iterate over the Saturdays and Sundays of the month
            while first_sat.month == month:
                weekends.add(first_sat)
                first_sat += timedelta(days=7)

            while first_sun.month == month:
                weekends.add(first_sun)
                first_sun += timedelta(days=7)

    return weekends
