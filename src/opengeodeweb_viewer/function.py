from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_schemas(params, schema):
    try:
        validate(instance=params, schema=schema)
    except ValidationError as e:
        print(400, f"Validation error: {e.message}")
