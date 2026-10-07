from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


class Location(Enum):
    CELL = "cell"
    POINT = "point"


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    item: int
    location: Location
    maximum: float
    minimum: float
    name: str


@dataclass
class Threshold(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: list[str]
    attribute: Attribute | None = None


@dataclass
class ThresholdResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



threshold_route = Route(
    schema=load_schema(Path(__file__)),
    params=Threshold,
    response=ThresholdResponse,
)

__all__ = ["Attribute", "Threshold", "ThresholdResponse", "threshold_route"]
