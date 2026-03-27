from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ColorClass(DataClassJsonMixin):
    b: int
    g: int
    r: int
    a: Optional[float] = None


@dataclass
class ComponentsColor(DataClassJsonMixin):
    block_ids: List[int]
    color: ColorClass
    id: str
