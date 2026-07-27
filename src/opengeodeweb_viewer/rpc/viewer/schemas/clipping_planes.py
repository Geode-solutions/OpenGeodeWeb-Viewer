from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class PlaneData(DataClassJsonMixin):
    origin: list[float]
    normal: list[float]


@dataclass
class ClippingPlanes(DataClassJsonMixin):
    ids: list[str]
    planes: list[PlaneData]
