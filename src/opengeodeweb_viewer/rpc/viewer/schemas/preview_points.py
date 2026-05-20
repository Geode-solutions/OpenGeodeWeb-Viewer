from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class Point(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    x: float
    y: float
    z: float


class Style(str, Enum):
    CURVE = "curve"
    POINTS = "points"


@dataclass
class PreviewPoints(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    points: List[Point]
    style: Style
