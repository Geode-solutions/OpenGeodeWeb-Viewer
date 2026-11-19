from opengeodeweb_microservice.schema_types import AttributeName, DataId
from opengeodeweb_viewer.schema_types import AttributeItem, AttributeRangeMaximum, AttributeRangeMinimum, ColorMapPoints, ColorRGBA
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import Optional


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: DataId
    item: AttributeItem
    maximum: AttributeRangeMaximum
    minimum: AttributeRangeMinimum
    name: AttributeName
    points: ColorMapPoints
    """Flat array of [value, r, g, b, ...]"""

    no_data_color: Optional[ColorRGBA] = None


@dataclass
class AttributeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


attribute_route = Route(
    schema=load_schema(Path(__file__)),
    params=Attribute,
    response=AttributeResponse,
)

__all__ = ["ColorRGBA", "Attribute", "AttributeResponse", "attribute_route"]
