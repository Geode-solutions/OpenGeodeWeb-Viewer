from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Axes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    visibility: bool


@dataclass
class AxesResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


axes_route = Route(
    schema=load_schema(__file__),
    params=Axes,
    response=AxesResponse,
)

__all__ = ["Axes", "AxesResponse", "axes_route"]
