from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from enum import Enum


@dataclass
class TextColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    b: int
    g: int
    r: int


class FontFamily(Enum):
    ARIAL = "arial"
    COURIER = "courier"
    TIMES = "times"


@dataclass
class SetTextStyle(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: TextColor
    font_family: FontFamily
    opacity: float


@dataclass
class SetTextStyleResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


set_text_style_route = Route(
    schema=load_schema(Path(__file__)),
    params=SetTextStyle,
    response=SetTextStyleResponse,
)

__all__ = ["TextColor", "SetTextStyle", "SetTextStyleResponse", "set_text_style_route"]
