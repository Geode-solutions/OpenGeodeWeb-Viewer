from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class PickedIDS(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: list[str]
    x: float
    y: float


@dataclass
class PickedIDSResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    array_ids: list[str]
    viewer_id: int | None = None


picked_ids_route = Route(
    schema=load_schema(Path(__file__)),
    params=PickedIDS,
    response=PickedIDSResponse,
)

__all__ = ["PickedIDS", "PickedIDSResponse", "picked_ids_route"]
