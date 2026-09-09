from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_viewer.rpc.mesh.schemas.color import ColorClass as NoDataColor


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    id: str
    block_ids: List[int]
    item: int
    maximum: float
    minimum: float
    name: str
    points: List[float]
    """Flat array of [value, r, g, b, ...]"""
    no_data_color: Optional[NoDataColor] = None
