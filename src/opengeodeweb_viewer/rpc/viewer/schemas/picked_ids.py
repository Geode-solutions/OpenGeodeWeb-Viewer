from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class PickedIDS(DataClassJsonMixin):
    ids: List[str]
    x: float
    y: float
