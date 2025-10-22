from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class ColorClass(DataClassJsonMixin):
    b: int
    g: int
    r: int


@dataclass
class Color(DataClassJsonMixin):
    color: ColorClass
    id: str
