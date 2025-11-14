from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class SetZScaling(DataClassJsonMixin):
    def __post_init__(self):
        print(self, flush=True)

    z_scale: float
