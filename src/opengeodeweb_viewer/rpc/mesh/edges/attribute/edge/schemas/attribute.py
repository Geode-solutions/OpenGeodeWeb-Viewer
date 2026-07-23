from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


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
