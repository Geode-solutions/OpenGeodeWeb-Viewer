from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class NoDataColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    alpha: float
    blue: int
    green: int
    red: int


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: list[int]
    id: str
    item: int
    maximum: float
    minimum: float
    name: str
    points: list[float]
    """Flat array of [value, r, g, b, ...]"""

    no_data_color: NoDataColor | None = None


@dataclass
class AttributeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



attribute_route = Route(
    schema=load_schema(Path(__file__)),
    params=Attribute,
    response=AttributeResponse,
)

__all__ = ["Attribute", "AttributeResponse", "NoDataColor", "attribute_route"]
