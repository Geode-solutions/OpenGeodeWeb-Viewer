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
