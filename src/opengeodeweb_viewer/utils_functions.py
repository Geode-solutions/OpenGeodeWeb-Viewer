import logging

# Standard library imports
# Third party imports
from typing import Protocol

import fastjsonschema  # type: ignore[import-untyped]
from opengeodeweb_microservice.schemas import SchemaDict
from vtkmodules.vtkRenderingCore import vtkColorTransferFunction

logger = logging.getLogger(__name__)


class ColorClassProtocol(Protocol):
    alpha: float
    blue: int
    green: int
    red: int


class AttributeProtocol(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def item(self) -> int: ...
    @property
    def points(self) -> list[float]: ...
    @property
    def minimum(self) -> float: ...
    @property
    def maximum(self) -> float: ...
    @property
    def no_data_color(self) -> ColorClassProtocol | None: ...


type RpcParams = dict[str, str]


def validate_schema(
    rpc_params: RpcParams, schema: SchemaDict, prefix: str = ""
) -> None:
    logger.debug("%s%s rpc_params=%s", prefix, schema["rpc"], rpc_params)
    try:
        validate = fastjsonschema.compile(schema)
        validate(rpc_params)
    except fastjsonschema.JsonSchemaException as e:
        logger.warning("Validation error: %s", e.message)
        raise ValueError(
            {
                "code": 400,
                "route": schema["rpc"],
                "name": "Bad request",
                "description": e.message,
            }
        ) from e


CIRCLE_DEGREES = 360
HASH_PRIME = 31
DEGREES_PER_STEP = 30
STEPS_COUNT = 12
BASE_LIGHTNESS = 0.5
VIBRANCY_RANGE = 0.35
MIRROR_MAX = 9
PHASE_GREEN = 8


def deterministic_color(identifier: str) -> tuple[float, float, float]:
    if not identifier:
        return (128 / 255, 128 / 255, 128 / 255)

    h = 0
    for ch in identifier:
        h = ord(ch) + h * HASH_PRIME

    hue = abs(h % CIRCLE_DEGREES)

    def component(phase: int) -> float:
        step = (phase + hue / DEGREES_PER_STEP) % STEPS_COUNT
        intensity = BASE_LIGHTNESS - VIBRANCY_RANGE * max(
            min(step - 3, MIRROR_MAX - step, 1), -1
        )
        return round(255 * intensity) / 255

    return (component(0), component(PHASE_GREEN), component(4))


def create_color_transfer_function(
    points: list[float],
    minimum: float,
    maximum: float,
    item: int = 0,
    no_data_color: ColorClassProtocol | None = None,
) -> vtkColorTransferFunction:
    lut = vtkColorTransferFunction()
    lut.SetVectorModeToComponent()
    lut.SetVectorComponent(item)
    lut.SetRange(minimum, maximum)
    if no_data_color:
        lut.SetNanColor(
            no_data_color.red / 255,
            no_data_color.green / 255,
            no_data_color.blue / 255,
        )
        lut.SetNanOpacity(float(no_data_color.alpha))
    if points:
        x_min, x_max = points[0], points[-4]
        span = x_max - x_min
        for i in range(0, len(points), 4):
            x, r, g, b = points[i : i + 4]
            new_x = (
                minimum + (x - x_min) / span * (maximum - minimum) if span else minimum
            )
            lut.AddRGBPoint(new_x, r, g, b)
    else:
        lut.AddRGBPoint(minimum, 0, 0, 0)
        lut.AddRGBPoint(maximum, 1, 1, 1)
    return lut
