from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Layer(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    crop: bool
    map: str
    opacity: float
    visible: bool


@dataclass
class BasemapLayers(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    layers: List[Layer]


@dataclass
class BasemapLayersResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


basemap_layers_route = Route(
    schema=load_schema(Path(__file__)),
    params=BasemapLayers,
    response=BasemapLayersResponse,
)

__all__ = ["Layer", "BasemapLayers", "BasemapLayersResponse", "basemap_layers_route"]
