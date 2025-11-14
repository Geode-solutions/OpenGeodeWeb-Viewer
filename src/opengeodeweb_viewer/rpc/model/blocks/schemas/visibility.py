from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class Visibility(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    block_ids: List[int]
    id: str
    visibility: bool
