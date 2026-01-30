from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PolygonColorMap(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    id: str
    points: List[float]
    """Flat array of [value, r, g, b, ...]"""

    maximum: Optional[float] = None
    minimum: Optional[float] = None
