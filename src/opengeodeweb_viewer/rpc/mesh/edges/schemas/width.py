from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Width(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    width: float


@dataclass
class WidthResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



width_route = Route(
    schema=load_schema(Path(__file__)),
    params=Width,
    response=WidthResponse,
)

__all__ = ["Width", "WidthResponse", "width_route"]
