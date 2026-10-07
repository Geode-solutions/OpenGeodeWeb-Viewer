from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


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

    data_id: str | None = None


pick_colormap_route = Route(
    schema=load_schema(Path(__file__)),
    params=PickColormap,
    response=PickColormapResponse,
)

__all__ = ["PickColormap", "PickColormapResponse", "pick_colormap_route"]
