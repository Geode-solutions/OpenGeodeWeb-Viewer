from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class Point(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    x: float
    y: float
    z: float


class Style(Enum):
    CURVE = "curve"
    POINTS = "points"
    SURFACE = "surface"


@dataclass
class PreviewPoints(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    points: List[Point]
    style: Style
    closed: Optional[bool] = None
