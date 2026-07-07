from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional


@dataclass
class Name(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    id: str
    name: str
    item: Optional[int] = None
