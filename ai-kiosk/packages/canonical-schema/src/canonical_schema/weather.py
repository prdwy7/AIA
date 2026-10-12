"""Weather snapshots (roadmap §9.3, §6.7 weather_snapshots).

IMD API data is cached (90 days) and polled every 15–60 min. Freshness SLOs:
forecast < 6 h, nowcast < 2 h. **STALE weather → spray window UNKNOWN**
(never guess a spray window from stale data).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import new_ulid
from .enums import SprayWindow, WeatherStatus


class WeatherSnapshot(BaseModel):
    """Cached IMD weather/agromet snapshot (roadmap §6.7)."""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    station_id: str
    location_name: str | None = None
    lat: float | None = None
    lon: float | None = None

    fetched_at: datetime = Field(description="When IMD data was fetched (UTC)")
    valid_from: datetime | None = None
    valid_to: datetime | None = None

    temperature_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    wind_speed_kmh: float | None = Field(default=None, ge=0)
    wind_direction: str | None = None
    rainfall_mm: float | None = Field(default=None, ge=0)
    forecast_hours: list[dict] = Field(
        default_factory=list, description="Hourly forecast entries (IMD schema)"
    )
    nowcast: dict | None = Field(default=None, description="Very short-range (IMD nowcast)")
    advisory: str | None = Field(default=None, description="KALP/SANKALP agromet advisory text")

    status: WeatherStatus = WeatherStatus.FRESH
    spray_window: SprayWindow = SprayWindow.UNKNOWN
    source_ref: str | None = Field(default=None, description="IMD API response reference")

    def is_stale(
        self, now: datetime, forecast_max_age_h: float = 6.0, nowcast_max_age_h: float = 2.0
    ) -> bool:
        """Freshness check (roadmap §16.2): forecast < 6 h, nowcast < 2 h."""
        age_h = (now - self.fetched_at).total_seconds() / 3600.0
        limit = nowcast_max_age_h if self.nowcast is not None else forecast_max_age_h
        return age_h > limit
