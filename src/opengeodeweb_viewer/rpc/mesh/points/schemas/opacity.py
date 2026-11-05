from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Opacity(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    opacity: float


@dataclass
class OpacityResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


opacity_route = Route(
    schema=load_schema(Path(__file__)),
    params=Opacity,
    response=OpacityResponse,
)

__all__ = ["Opacity", "OpacityResponse", "opacity_route"]
