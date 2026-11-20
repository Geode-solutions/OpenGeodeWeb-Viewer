from opengeodeweb_viewer.schema_types import AttributeItem, AttributeRangeMaximum, AttributeRangeMinimum
from opengeodeweb_microservice.schema_types import DataId
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass
from typing import List


class Location(Enum):
    CELL = "cell"
    POINT = "point"


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    item: AttributeItem
    location: Location
    maximum: AttributeRangeMaximum
    minimum: AttributeRangeMinimum
    name: str


@dataclass
class Threshold(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    attributes: List[Attribute]
    ids: List[DataId]


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
