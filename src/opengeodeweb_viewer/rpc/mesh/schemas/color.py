from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class ColorClass(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    alpha: float
    blue: int
    green: int
    red: int


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    color: ColorClass
    id: str
