from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    b: int
    g: int
    r: int


@dataclass
class SetBackgroundColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: Color


@dataclass
class SetBackgroundColorResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


set_background_color_route = Route(
    schema=load_schema(__file__),
    params=SetBackgroundColor,
    response=SetBackgroundColorResponse,
)

__all__ = ["Color", "SetBackgroundColor", "SetBackgroundColorResponse", "set_background_color_route"]
