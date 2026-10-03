"""Chapter 25 solution: GitHub Actions cron runs in UTC and knows nothing about daylight saving time.

07:00 in Jerusalem is 04:00 UTC in summer (IDT, UTC+3) and 05:00 UTC in winter (IST, UTC+2).
Either schedule both lines and let the job skip the wrong one, or accept a one-hour drift twice a year.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

JERUSALEM = ZoneInfo("Asia/Jerusalem")


@dataclass(frozen=True)
class CronPlan:
    local_time: str
    summer_cron: str  # UTC cron while daylight saving time is in effect
    winter_cron: str
    note: str


def utc_hour_for(local_hour: int, local_minute: int, on: dt.date, tz: ZoneInfo = JERUSALEM) -> tuple[int, int]:
    local = dt.datetime(on.year, on.month, on.day, local_hour, local_minute, tzinfo=tz)
    utc = local.astimezone(dt.UTC)
    return utc.hour, utc.minute


def cron_for_local_time(local_hour: int, local_minute: int = 0, tz: ZoneInfo = JERUSALEM, year: int | None = None) -> CronPlan:
    """Two cron lines, one per DST regime, computed from real dates (15 July and 15 January)."""
    year = year or dt.datetime.now(tz=dt.UTC).year
    sh, sm = utc_hour_for(local_hour, local_minute, dt.date(year, 7, 15), tz)
    wh, wm = utc_hour_for(local_hour, local_minute, dt.date(year, 1, 15), tz)
    return CronPlan(
        local_time=f"{local_hour:02d}:{local_minute:02d} {tz.key}",
        summer_cron=f"{sm} {sh} * * *",
        winter_cron=f"{wm} {wh} * * *",
        note="GitHub Actions cron is UTC and ignores DST. Schedule both lines; the job checks the local hour and exits early on the wrong one.",
    )


def is_local_hour(now_utc: dt.datetime, local_hour: int, tz: ZoneInfo = JERUSALEM) -> bool:
    """The early-exit check the job runs: is it really `local_hour` o'clock where the reader lives?"""
    return now_utc.astimezone(tz).hour == local_hour
