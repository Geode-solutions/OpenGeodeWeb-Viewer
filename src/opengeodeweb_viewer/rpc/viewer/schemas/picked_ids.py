from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class PickedIDS(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    ids: List[str]
    x: float
    y: float
