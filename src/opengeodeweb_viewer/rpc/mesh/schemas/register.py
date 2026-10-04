from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


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

    pass


register_route = Route(
    schema=load_schema(__file__),
    params=Register,
    response=RegisterResponse,
)

__all__ = ["Register", "RegisterResponse", "register_route"]
