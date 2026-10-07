from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class ColorClass(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    alpha: float
    blue: int
    green: int
    red: int


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: ColorClass
    id: str


@dataclass
class ColorResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



color_route = Route(
    schema=load_schema(Path(__file__)),
    params=Color,
    response=ColorResponse,
)

__all__ = ["Color", "ColorClass", "ColorResponse", "color_route"]
