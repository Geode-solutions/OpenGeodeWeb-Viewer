from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


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
    schema=load_schema(__file__),
    params=GetPointPosition,
    response=GetPointPositionResponse,
)

__all__ = ["GetPointPosition", "GetPointPositionResponse", "get_point_position_route"]
