from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Size(DataClassJsonMixin):
    def __post_init__(self):
        print(self, flush=True)

    id: str
    size: float
