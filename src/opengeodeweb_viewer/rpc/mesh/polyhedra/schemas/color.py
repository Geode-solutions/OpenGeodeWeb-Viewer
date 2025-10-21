from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional


@dataclass
class ColorClass(DataClassJsonMixin):
    b: int
    g: int
    r: int
    a: Optional[float] = None


@dataclass
class Color(DataClassJsonMixin):
    color: ColorClass
    id: str
