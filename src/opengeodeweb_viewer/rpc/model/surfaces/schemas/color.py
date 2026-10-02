from opengeodeweb_microservice.schemas import Route, load_schema
from typing import List
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


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

    block_ids: List[int]
    color_mode: ColorMode
    id: str
    collection_id: Optional[str] = None
    color: Optional[ColorClass] = None


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

    colors: List[ColorResult]


color_route = Route(
    schema=load_schema(__file__),
    params=Color,
    response=ColorResponse,
)

__all__ = ["ColorClass", "Color", "ColorResponse", "color_route"]
