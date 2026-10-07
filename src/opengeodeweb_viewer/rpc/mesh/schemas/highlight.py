from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Highlight(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    visibility: bool


@dataclass
class HighlightResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



highlight_route = Route(
    schema=load_schema(Path(__file__)),
    params=Highlight,
    response=HighlightResponse,
)

__all__ = ["Highlight", "HighlightResponse", "highlight_route"]
