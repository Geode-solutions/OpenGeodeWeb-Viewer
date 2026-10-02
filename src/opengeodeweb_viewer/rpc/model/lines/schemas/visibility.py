from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Visibility(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: List[int]
    id: str
    visibility: bool
