from dataclasses_json import DataClassJsonMixin
from enum import Enum
from dataclasses import dataclass
from typing import List


class FieldType(Enum):
    CELLS = "cells"
    POINTS = "points"


@dataclass
class AttributeName(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    block_ids: List[int]
    field_type: FieldType
    id: str
    name: str
