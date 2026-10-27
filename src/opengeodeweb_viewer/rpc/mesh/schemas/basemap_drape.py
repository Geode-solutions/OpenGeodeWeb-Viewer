from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class BasemapDrape(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    around: bool
    data_ids: List[str]
    id: str


@dataclass
class BasemapDrapeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


basemap_drape_route = Route(
    schema=load_schema(Path(__file__)),
    params=BasemapDrape,
    response=BasemapDrapeResponse,
)

__all__ = ["BasemapDrape", "BasemapDrapeResponse", "basemap_drape_route"]
