from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Plane(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    normal: list[float]
    origin: list[float]


@dataclass
class ClippingPlanes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: list[str]
    planes: list[Plane]


@dataclass
class ClippingPlanesResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



clipping_planes_route = Route(
    schema=load_schema(Path(__file__)),
    params=ClippingPlanes,
    response=ClippingPlanesResponse,
)

__all__ = ["ClippingPlanes", "ClippingPlanesResponse", "Plane", "clipping_planes_route"]
