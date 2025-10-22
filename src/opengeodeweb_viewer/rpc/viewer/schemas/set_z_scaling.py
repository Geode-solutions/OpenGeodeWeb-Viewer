from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class SetZScaling(DataClassJsonMixin):
    z_scale: float
