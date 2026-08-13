from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Ruler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    enabled: Optional[bool] = None
    point1: Optional[List[float]] = None
    point2: Optional[List[float]] = None
