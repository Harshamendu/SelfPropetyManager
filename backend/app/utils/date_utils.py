from datetime import date, datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def start_of_year(year: int) -> date:
    return date(year, 1, 1)


def end_of_year(year: int) -> date:
    return date(year, 12, 31)
