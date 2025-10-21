from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Color(DataClassJsonMixin):
    b: int
    g: int
    r: int


@dataclass
class SetBackgroundColor(DataClassJsonMixin):
    color: Color
