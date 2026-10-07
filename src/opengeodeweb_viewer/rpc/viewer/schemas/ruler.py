from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Ruler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    points: list[list[float]]


@dataclass
class RulerResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    distance: float
    point1: list[float]
    point2: list[float] | None = None


ruler_route = Route(
    schema=load_schema(Path(__file__)),
    params=Ruler,
    response=RulerResponse,
)

__all__ = ["Ruler", "RulerResponse", "ruler_route"]
