# Standard library imports
import os
import json

# Third party imports
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Local application imports


def get_schemas_dict(path):
    json_files = os.listdir(path)
    schemas_dict = {}
    for json_file in json_files:
        last_point = json_file.rfind(".")
        filename = json_file[: -len(json_file) + last_point]
        with open(os.path.join(path, json_file), "r") as file:
            file_content = json.load(file)
            schemas_dict[filename] = file_content
    return schemas_dict


def validate_schema(params, schema, prefix=""):
    print(f"{prefix}{schema['rpc']}", f"{params=}", flush=True)
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
