# Standard library imports

# Third party imports
import fastjsonschema  # type: ignore

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
