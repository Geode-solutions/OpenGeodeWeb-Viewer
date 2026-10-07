from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from typing import List, Optional
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class PickedIDS(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: List[str]
    x: float
    y: float


@dataclass
class PickedIDSResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    array_ids: List[str]
    viewer_id: Optional[int] = None


picked_ids_route = Route(
    schema=load_schema(Path(__file__)),
    params=PickedIDS,
    response=PickedIDSResponse,
)

__all__ = ["PickedIDS", "PickedIDSResponse", "picked_ids_route"]
