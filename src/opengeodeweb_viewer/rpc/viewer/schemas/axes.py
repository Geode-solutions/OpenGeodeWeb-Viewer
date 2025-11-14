from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Axes(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    visibility: bool
