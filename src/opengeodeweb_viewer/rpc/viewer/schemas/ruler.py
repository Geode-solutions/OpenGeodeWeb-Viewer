from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Ruler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    point1: Optional[List[float]] = None
    point2: Optional[List[float]] = None
