from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class ColorMap(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    block_ids: List[int]
    id: str
    maximum: float
    minimum: float
    points: List[float]
    """Flat array of [value, r, g, b, ...]"""
