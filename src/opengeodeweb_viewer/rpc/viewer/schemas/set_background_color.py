from opengeodeweb_viewer.schema_types import ColorRGB
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class SetBackgroundColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: ColorRGB


@dataclass
class SetBackgroundColorResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


set_background_color_route = Route(
    schema=load_schema(Path(__file__)),
    params=SetBackgroundColor,
    response=SetBackgroundColorResponse,
)

__all__ = ["ColorRGB", "SetBackgroundColor", "SetBackgroundColorResponse", "set_background_color_route"]
