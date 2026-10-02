from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass
from typing import List


class FieldType(Enum):
    CELL = "CELL"
    POINT = "POINT"


@dataclass
class Highlight(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    field_type: FieldType
    ids: List[str]
    x: float
    y: float
