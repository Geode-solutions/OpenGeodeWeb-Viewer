from opengeodeweb_microservice.schemas import Route, load_schema
from typing import Dict, List, Union, Optional
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


class PickedFieldType(Enum):
    CELL = "CELL"
    POINT = "POINT"


@dataclass
class HighlightResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    attributes: Optional[Dict[str, Union[float, List[float]]]] = None
    field_type: Optional[PickedFieldType] = None
    geode_id: Optional[str] = None
    id: Optional[str] = None
    picked_id: Optional[int] = None


highlight_route = Route(
    schema=load_schema(__file__),
    params=Highlight,
    response=HighlightResponse,
)

__all__ = ["Highlight", "HighlightResponse", "highlight_route"]
