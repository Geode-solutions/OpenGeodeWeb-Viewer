from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Plane(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    normal: List[float]
    origin: List[float]


@dataclass
class ClippingPlanes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: List[str]
    planes: List[Plane]


@dataclass
class ClippingPlanesResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


clipping_planes_route = Route(
    schema=load_schema(Path(__file__)),
    params=ClippingPlanes,
    response=ClippingPlanesResponse,
)

__all__ = ["Plane", "ClippingPlanes", "ClippingPlanesResponse", "clipping_planes_route"]
