"""Zodiac-Meridian Router — astrologically-aware bus routing."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

from compute.body_wisdom import CRANIAL_NERVES

# Zodiac sign boundaries (ecliptic longitude degrees)
_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
_SIGN_TO_NERVE = {cn["zodiac"]: cn for cn in CRANIAL_NERVES}
_VERNAL_EQUINOX_2000 = datetime(2000, 3, 20, 7, 35, tzinfo=timezone.utc)


@dataclass
class RouteResult:
    bus_topic: str
    priority: float
    nerve: str
    sign: str


class ZodiacRouter:
    def current_sign(self, dt: datetime | None = None) -> str:
        dt = dt or datetime.now(timezone.utc)
        day_of_year = dt.timetuple().tm_yday
        # Simple approximation: Aries starts ~March 21 (day 80)
        ecliptic_day = (day_of_year - 80) % 365
        sign_idx = int(ecliptic_day / 30.44) % 12
        return _SIGNS[sign_idx]

    def route(self, message: str, dt: datetime | None = None) -> RouteResult:
        sign = self.current_sign(dt)
        nerve = _SIGN_TO_NERVE[sign]
        priority = 1.0 + (len(message) % 9) / 9.0  # 1.0-1.89 based on message
        return RouteResult(bus_topic=nerve["bus"], priority=round(priority, 2), nerve=nerve["nerve"], sign=sign)

    def get_active_meridians(self, dt: datetime | None = None) -> list[str]:
        sign = self.current_sign(dt)
        nerve = _SIGN_TO_NERVE[sign]
        # Adjacent signs also partially active
        idx = _SIGNS.index(sign)
        active = [_SIGNS[idx], _SIGNS[(idx + 1) % 12], _SIGNS[(idx - 1) % 12]]
        return [_SIGN_TO_NERVE[s]["bus"] for s in active]
