from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass


class OutputExtension(Enum):
    JPG = "jpg"
    PNG = "png"


@dataclass
class TakeScreenshot(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    filename: str
    include_background: bool
    output_extension: OutputExtension
