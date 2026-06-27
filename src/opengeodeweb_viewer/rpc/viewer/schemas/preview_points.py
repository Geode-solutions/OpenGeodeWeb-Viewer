from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class Point(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

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
        print(self, flush=True)

    points: List[Point]
    style: Style
    closed: Optional[bool] = None
