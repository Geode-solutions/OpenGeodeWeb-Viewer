from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_schemas(params, schema):
    try:
        validate(instance=params, schema=schema)
    except ValidationError as e:
        print(f"Validation error: {e.message}", flush=True)
        raise Exception(
            {
                "code": 400,
                "route": schema["rpc"],
                "name": "Bad request",
                "description": e.message,
            }
        )
