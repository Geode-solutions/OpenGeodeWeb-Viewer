from opengeodeweb_viewer.schema_types import ColorRGB, Opacity
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from enum import Enum


class FontFamily(Enum):
    ARIAL = "arial"
    COURIER = "courier"
    TIMES = "times"


@dataclass
class SetTextStyle(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: ColorRGB
    font_family: FontFamily
    opacity: Opacity


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

__all__ = ["ColorRGB", "SetTextStyle", "SetTextStyleResponse", "set_text_style_route"]
