# Standard library imports
import os
import json

# Third party imports
import fastjsonschema
from fastjsonschema import JsonSchemaException

type JsonPrimitive = str | int | float | bool
type JsonValue = JsonPrimitive | dict[str, JsonValue] | list[JsonValue]
type RpcParams = dict[str, JsonValue]

type ColorDict = dict[str, int]
type RpcParamsWithColor = dict[str, JsonPrimitive | ColorDict]
type RpcParamsWithList = dict[str, JsonPrimitive | list[str]]
type RpcTestParams = list[
    dict[str, str | int | float | bool | dict[str, int] | list[str]] | int
] | None


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


def validate_schema(params: RpcParams, schema: dict, prefix: str = "") -> None:
    print(f"{prefix}{schema['rpc']}", f"{params=}", flush=True)
    try:
        validate = fastjsonschema.compile(schema)
        validate(params)
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
