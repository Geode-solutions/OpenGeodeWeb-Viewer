from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Axes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    visibility: bool


@dataclass
class AxesResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



axes_route = Route(
    schema=load_schema(Path(__file__)),
    params=Axes,
    response=AxesResponse,
)

__all__ = ["Axes", "AxesResponse", "axes_route"]
