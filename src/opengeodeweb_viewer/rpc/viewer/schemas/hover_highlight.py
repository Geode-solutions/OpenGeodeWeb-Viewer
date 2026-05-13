from dataclasses_json import DataClassJsonMixin
from enum import Enum
from dataclasses import dataclass
from typing import List


class FieldType(Enum):
    CELL = "CELL"
    POINT = "POINT"


@dataclass
class HoverHighlight(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    field_type: FieldType
    ids: List[str]
    x: float
    y: float
