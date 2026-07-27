from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class PlaneData(DataClassJsonMixin):
    origin: list[float]
    normal: list[float]


@dataclass
class ClippingPlanes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    ids: list[str]
    planes: list[PlaneData]
