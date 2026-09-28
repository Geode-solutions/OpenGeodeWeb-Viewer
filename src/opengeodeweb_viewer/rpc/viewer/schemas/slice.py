from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Slice(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    ids: List[str]
    index: int
    axis: Optional[int] = None
