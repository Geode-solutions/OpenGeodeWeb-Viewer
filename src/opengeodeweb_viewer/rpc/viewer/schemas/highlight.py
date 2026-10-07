from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


class FieldType(Enum):
    CELL = "CELL"
    POINT = "POINT"


@dataclass
class Highlight(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    field_type: FieldType
    ids: list[str]
    x: float
    y: float


class PickedFieldType(Enum):
    CELL = "CELL"
    POINT = "POINT"


@dataclass
class HighlightResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    attributes: dict[str, float | list[float]] | None = None
    field_type: PickedFieldType | None = None
    geode_id: str | None = None
    id: str | None = None
    picked_id: int | None = None


highlight_route = Route(
    schema=load_schema(Path(__file__)),
    params=Highlight,
    response=HighlightResponse,
)

__all__ = ["Highlight", "HighlightResponse", "highlight_route"]
