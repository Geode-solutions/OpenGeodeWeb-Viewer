from opengeodeweb_viewer.schema_types import BlockIds, ColorRGBA
from opengeodeweb_microservice.schema_types import DataId, GeodeId, ViewerId
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from typing import List
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ColorMode(Enum):
    CONSTANT = "constant"
    RANDOM = "random"


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: BlockIds
    color_mode: ColorMode
    id: DataId
    collection_id: Optional[GeodeId] = None
    color: Optional[ColorRGBA] = None


@dataclass
class ColorResult(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: ColorRGBA
    geode_id: GeodeId
    viewer_id: ViewerId


@dataclass
class ColorResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    colors: List[ColorResult]


color_route = Route(
    schema=load_schema(Path(__file__)),
    params=Color,
    response=ColorResponse,
)

__all__ = ["ColorRGBA", "Color", "ColorResponse", "color_route"]
