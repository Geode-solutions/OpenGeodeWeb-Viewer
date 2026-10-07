from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Highlight(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: List[int]
    id: str
    visibility: bool


@dataclass
class HighlightResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


highlight_route = Route(
    schema=load_schema(Path(__file__)),
    params=Highlight,
    response=HighlightResponse,
)

__all__ = ["Highlight", "HighlightResponse", "highlight_route"]
