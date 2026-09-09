from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List, Optional


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
    points: List[float]
    """Flat array of [value, r, g, b, ...]"""

    no_data_color: Optional[NoDataColor] = None
