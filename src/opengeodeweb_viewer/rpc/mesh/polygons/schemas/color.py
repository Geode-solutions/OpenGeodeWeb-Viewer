from opengeodeweb_viewer.schema_types import ColorRGBA
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: ColorRGBA
    id: str


@dataclass
class ColorResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


color_route = Route(
    schema=load_schema(Path(__file__)),
    params=Color,
    response=ColorResponse,
)

__all__ = ["ColorRGBA", "Color", "ColorResponse", "color_route"]
