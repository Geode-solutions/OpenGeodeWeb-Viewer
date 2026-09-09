from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class NoDataColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    alpha: float
    blue: int
    green: int
    red: int


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    id: str
    item: int
    maximum: float
    minimum: float
    name: str
    no_data: bool
    no_data_color: NoDataColor
    points: List[float]
    """Flat array of [value, r, g, b, ...]"""
