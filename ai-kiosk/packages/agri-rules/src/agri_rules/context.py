"""Evaluation context for the rules engine (roadmap §6.5).

Rules are deterministic predicates over a flat, namespaced context:
`case.*`, `decision.*`, `weather.*`, `regulatory.*`. The context is built
from the case graph + decision draft + weather snapshot + regulatory table —
never from free LLM text.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CaseContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    crop: str | None = None
    variety: str | None = None
    stage: str | None = None
    region: str | None = None
    season: str | None = None


class DecisionContext(BaseModel):
    """The decision draft under evaluation (roadmap §6.1 decision payload)."""

    model_config = ConfigDict(frozen=True)

    product_id: str | None = None
    active_ingredient: str | None = None
    formulation: str | None = None
    dose_value: float | None = Field(default=None, ge=0)
    dose_unit: str | None = None
    dose_min: float | None = Field(default=None, ge=0, description="Approved minimum")
    dose_max: float | None = Field(default=None, ge=0, description="Approved maximum")
    method: str | None = None
    timing: str | None = None
    phi_days: int | None = Field(default=None, ge=0, description="Pre-harvest interval")
    days_to_harvest: int | None = Field(default=None, ge=0)
    ppe: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class WeatherContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str = Field(default="UNKNOWN", description="FRESH | STALE | UNKNOWN")
    spray_window: str = Field(default="UNKNOWN", description="OPEN | CLOSED | UNKNOWN")
    wind_speed_kmh: float | None = Field(default=None, ge=0)
    rainfall_mm: float | None = Field(default=None, ge=0)


class RegulatoryContext(BaseModel):
    """PPQS/CIB&RC status for the product under evaluation."""

    model_config = ConfigDict(frozen=True)

    status: str = Field(
        default="permitted", description="banned | refused | restricted | permitted"
    )
    restrictions: str | None = Field(
        default=None, description="Crop/region/dose limits for restricted"
    )


class RuleContext(BaseModel):
    """Full evaluation context (roadmap §6.5)."""

    model_config = ConfigDict(frozen=True)

    case: CaseContext = Field(default_factory=CaseContext)
    decision: DecisionContext = Field(default_factory=DecisionContext)
    weather: WeatherContext = Field(default_factory=WeatherContext)
    regulatory: RegulatoryContext = Field(default_factory=RegulatoryContext)

    def as_flat(self) -> dict[str, Any]:
        """Flatten to `namespace.field` keys for the predicate language."""
        flat: dict[str, Any] = {}
        for ns, sub in (
            ("case", self.case),
            ("decision", self.decision),
            ("weather", self.weather),
            ("regulatory", self.regulatory),
        ):
            for k, v in sub.model_dump().items():
                flat[f"{ns}.{k}"] = v
        return flat
