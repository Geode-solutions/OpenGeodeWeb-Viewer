from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class GridScale(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    visibility: bool


@dataclass
class GridScaleResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


grid_scale_route = Route(
    schema=load_schema(__file__),
    params=GridScale,
    response=GridScaleResponse,
)

__all__ = ["GridScale", "GridScaleResponse", "grid_scale_route"]
