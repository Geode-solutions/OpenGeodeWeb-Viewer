from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass


class Marker(Enum):
    AXES = "axes"
    COMPASS = "compass"


@dataclass
class SetOrientationWidget(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    marker: Marker


@dataclass
class SetOrientationWidgetResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


set_orientation_widget_route = Route(
    schema=load_schema(Path(__file__)),
    params=SetOrientationWidget,
    response=SetOrientationWidgetResponse,
)

__all__ = ["SetOrientationWidget", "SetOrientationWidgetResponse", "set_orientation_widget_route"]
