from opengeodeweb_microservice.schemas import Route, load_schema
from typing import List, Optional
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Ruler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    points: List[List[float]]


@dataclass
class RulerResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    distance: float
    point1: List[float]
    point2: Optional[List[float]] = None


ruler_route = Route(
    schema=load_schema(__file__),
    params=Ruler,
    response=RulerResponse,
)

__all__ = ["Ruler", "RulerResponse", "ruler_route"]
