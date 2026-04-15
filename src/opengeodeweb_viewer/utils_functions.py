# Standard library imports

# Third party imports
import fastjsonschema  # type: ignore
import math

from opengeodeweb_microservice.schemas import SchemaDict

type RpcParams = dict[str, str]


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
        intensity = BASE_LIGHTNESS - VIBRANCY_RANGE * max(min(step - 3, MIRROR_MAX - step, 1), -1)
        return round(255 * intensity) / 255

    return (component(0), component(PHASE_GREEN), component(4))