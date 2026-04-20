from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class ColorClass(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    a: float
    b: int
    g: int
    r: int
    a: float


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    color: ColorClass
    id: str
