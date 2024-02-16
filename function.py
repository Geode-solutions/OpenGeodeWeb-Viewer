import os
import json
import jsonschema
from jsonschema import validate


def validate_schemas(params, schema):
    try:
        validate(instance=params, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        print(400, f"Validation error: {e.message}")
