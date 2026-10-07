from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Register(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    name: str


@dataclass
class RegisterResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



register_route = Route(
    schema=load_schema(Path(__file__)),
    params=Register,
    response=RegisterResponse,
)

__all__ = ["Register", "RegisterResponse", "register_route"]
