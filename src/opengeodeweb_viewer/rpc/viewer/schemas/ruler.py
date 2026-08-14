from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class Ruler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    points: List[List[float]]
