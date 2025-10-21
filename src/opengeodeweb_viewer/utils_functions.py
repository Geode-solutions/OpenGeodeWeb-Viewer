# Standard library imports
import os
import glob
import json

# Third party imports
import fastjsonschema  # type: ignore

type JsonPrimitive = str | int | float | bool
type JsonValue = JsonPrimitive | dict[str, JsonValue] | list[JsonValue]
type RpcParams = dict[str, JsonValue]

type ColorDict = dict[str, int]
type RpcParamsWithColor = dict[str, JsonPrimitive | ColorDict]
type RpcParamsWithList = dict[str, JsonPrimitive | list[str]]

type SchemaDict = dict[str, str]


def get_schemas_dict(path: str) -> dict[str, SchemaDict]:
    schemas_dict: dict[str, SchemaDict] = {}
    for json_file in glob.glob(os.path.join(path, "*.json")):
        filename = os.path.basename(json_file)
        with open(os.path.join(path, json_file), "r") as file:
            file_content = json.load(file)
            schemas_dict[os.path.splitext(filename)[0]] = file_content
    return schemas_dict


def validate_schema(params: RpcParams, schema: SchemaDict, prefix: str = "") -> None:
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
