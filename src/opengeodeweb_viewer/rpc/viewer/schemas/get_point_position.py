from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class GetPointPosition(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    x: int
    y: int
