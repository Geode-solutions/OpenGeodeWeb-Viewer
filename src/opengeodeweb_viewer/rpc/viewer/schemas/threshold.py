from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


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

    ids: List[str]
    attribute: Optional[Attribute] = None


@dataclass
class ThresholdResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


threshold_route = Route(
    schema=load_schema(Path(__file__)),
    params=Threshold,
    response=ThresholdResponse,
)

__all__ = ["Attribute", "Threshold", "ThresholdResponse", "threshold_route"]
