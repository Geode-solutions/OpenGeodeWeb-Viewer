from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List, Optional


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

    block_ids: List[int]
    id: str
    item: int
    maximum: float
    minimum: float
    name: str
    points: List[float]
    """Flat array of [value, r, g, b, ...]"""

    no_data_color: Optional[NoDataColor] = None


@dataclass
class AttributeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


attribute_route = Route(
    schema=load_schema(__file__),
    params=Attribute,
    response=AttributeResponse,
)

__all__ = ["NoDataColor", "Attribute", "AttributeResponse", "attribute_route"]
