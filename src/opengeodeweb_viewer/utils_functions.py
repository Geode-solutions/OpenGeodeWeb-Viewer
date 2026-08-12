# Standard library imports

# Third party imports
import fastjsonschema  # type: ignore
import functools
import math
from typing import Any, Callable, TypeVar
from wslink import register  # type: ignore
from vtkmodules.vtkRenderingCore import vtkColorTransferFunction

from opengeodeweb_microservice.schemas import SchemaDict

type RpcParams = dict[str, str]

R = TypeVar("R")


def exportRpc(rpc_id: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    def decorator(function: Callable[..., R]) -> Callable[..., R]:
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
            do_stream = bool(kwargs.pop("stream", False))
            print("do_stream", do_stream, flush=True)
            result = function(self, *args, **kwargs)
            if do_stream:
                rpc_params = args[0] if args else None
                self.publish(rpc_id, rpc_params)
            return result

        return register(rpc_id)(wrapper)  # type: ignore[no-any-return]

    return decorator


def validate_schema(
    rpc_params: RpcParams, schema: SchemaDict, prefix: str = ""
) -> None:
    print(f"{prefix}{schema['rpc']}", f"{rpc_params=}", flush=True)
    try:
        validate = fastjsonschema.compile(schema)
        validate(rpc_params)
    except fastjsonschema.JsonSchemaException as e:
        print(f"Validation error: {e.message}", flush=True)
        raise Exception(
            {
                "code": 400,
                "route": schema["rpc"],
                "name": "Bad request",
                "description": e.message,
            }
        )


def deterministic_color(identifier: str) -> tuple[float, float, float]:
    CIRCLE_DEGREES = 360
    HASH_PRIME = 31
    DEGREES_PER_STEP = 30
    STEPS_COUNT = 12
    BASE_LIGHTNESS = 0.5
    VIBRANCY_RANGE = 0.35
    MIRROR_MAX = 9
    PHASE_GREEN = 8

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
    points: list[float], minimum: float, maximum: float, item: int = 0
) -> vtkColorTransferFunction:
    lut = vtkColorTransferFunction()
    lut.SetVectorModeToComponent()
    lut.SetVectorComponent(item)
    lut.SetRange(minimum, maximum)
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
