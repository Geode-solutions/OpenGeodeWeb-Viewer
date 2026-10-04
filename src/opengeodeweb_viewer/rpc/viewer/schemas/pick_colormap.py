from opengeodeweb_microservice.schemas import Route, load_schema
from typing import Optional
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class PickColormap(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    x: float
    y: float


@dataclass
class PickColormapResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    data_id: Optional[str] = None


pick_colormap_route = Route(
    schema=load_schema(__file__),
    params=PickColormap,
    response=PickColormapResponse,
)

__all__ = ["PickColormap", "PickColormapResponse", "pick_colormap_route"]
