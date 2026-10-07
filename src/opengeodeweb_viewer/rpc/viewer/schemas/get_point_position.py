from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class GetPointPosition(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    x: int
    y: int


@dataclass
class GetPointPositionResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    x: float
    y: float
    z: float


get_point_position_route = Route(
    schema=load_schema(Path(__file__)),
    params=GetPointPosition,
    response=GetPointPositionResponse,
)

__all__ = ["GetPointPosition", "GetPointPositionResponse", "get_point_position_route"]
