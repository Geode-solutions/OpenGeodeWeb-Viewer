from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class Plane(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    normal: List[float]
    origin: List[float]


@dataclass
class ClippingPlanes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    ids: List[str]
    planes: List[Plane]
