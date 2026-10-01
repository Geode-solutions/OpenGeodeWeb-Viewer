from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    b: int
    g: int
    r: int


@dataclass
class SetBackgroundColor(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    color: Color
