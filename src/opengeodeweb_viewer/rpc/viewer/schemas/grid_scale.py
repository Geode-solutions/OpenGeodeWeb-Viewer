from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class GridScale(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    visibility: bool


@dataclass
class GridScaleResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



grid_scale_route = Route(
    schema=load_schema(Path(__file__)),
    params=GridScale,
    response=GridScaleResponse,
)

__all__ = ["GridScale", "GridScaleResponse", "grid_scale_route"]
