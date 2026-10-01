from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Deregister(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
