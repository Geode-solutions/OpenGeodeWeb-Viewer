from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Name(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    block_ids: List[int]
    id: str
    name: str
    item: Optional[int] = None
