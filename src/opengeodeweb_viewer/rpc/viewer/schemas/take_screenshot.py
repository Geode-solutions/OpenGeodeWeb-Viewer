from dataclasses_json import DataClassJsonMixin
from enum import Enum
from dataclasses import dataclass


class OutputExtension(Enum):
    JPG = "jpg"
    PNG = "png"


@dataclass
class TakeScreenshot(DataClassJsonMixin):
    filename: str
    include_background: bool
    output_extension: OutputExtension
