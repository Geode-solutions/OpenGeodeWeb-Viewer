from dataclasses import dataclass
from enum import Enum
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


class ColorMode(Enum):
    CONSTANT = "constant"
    RANDOM = "random"


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: list[int]
    color_mode: ColorMode
    id: str
    collection_id: str | None = None
    color: ColorClass | None = None


@dataclass
class ColorRGBA(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    alpha: float
    blue: int
    green: int
    red: int


@dataclass
class ColorResult(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: ColorRGBA
    geode_id: str
    viewer_id: int


@dataclass
class ColorResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    colors: list[ColorResult]


color_route = Route(
    schema=load_schema(Path(__file__)),
    params=Color,
    response=ColorResponse,
)

__all__ = ["Color", "ColorClass", "ColorResponse", "color_route"]
