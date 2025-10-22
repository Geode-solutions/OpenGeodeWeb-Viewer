from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class Visibility(DataClassJsonMixin):
    block_ids: List[int]
    id: str
    visibility: bool
