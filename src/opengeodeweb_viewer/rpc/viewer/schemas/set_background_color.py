from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    b: int
    g: int
    r: int


@dataclass
class SetBackgroundColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    color: Color
