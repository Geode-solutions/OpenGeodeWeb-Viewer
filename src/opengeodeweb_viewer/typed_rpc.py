# Standard library imports
import functools
import os
from dataclasses import fields
from typing import TYPE_CHECKING, Any, Concatenate, Protocol, cast

# Third party imports
import fastjsonschema  # type: ignore[import-untyped]
from dataclasses_json import DataClassJsonMixin
from wslink import register  # type: ignore[import-untyped]

# Local application imports
from opengeodeweb_viewer.utils_functions import RpcParams, validate_schema

if TYPE_CHECKING:
    from collections.abc import Callable

    from opengeodeweb_microservice.schemas import Route

TYPED_RPC_MARKER = "__typed_rpc__"


class Publisher(Protocol):
    def publish(self, topic: str, data: object) -> None: ...


def _drop_none(value: object) -> object:
    # Optional response fields are generated as `field: X | None = None`:
    # omit them instead of sending null
    if isinstance(value, dict):
        return {key: _drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_drop_none(item) for item in value]
    return value


def _to_payload(result: DataClassJsonMixin) -> dict[str, Any]:
    payload = cast("dict[str, Any]", _drop_none(result.to_dict(encode_json=True)))
    # dataclasses_json encodes bytes as a list of ints: keep them as bytes,
    # wslink (msgpack) sends them as binary
    for field in fields(result):  # type: ignore[arg-type]
        value = getattr(result, field.name)
        if isinstance(value, bytes):
            payload[field.name] = value
    return payload


def _validate_responses() -> bool:
    return os.environ.get("PYTHON_ENV", "prod").strip().lower() in ("dev", "test")


def typed_rpc[SelfT: Publisher, ParamsT: DataClassJsonMixin, ResponseT: DataClassJsonMixin](
    prefix: str, route: Route[ParamsT, ResponseT]
) -> Callable[
    [Callable[[SelfT, ParamsT], ResponseT]],
    Callable[Concatenate[SelfT, ...], dict[str, Any]],
]:
    """Register a wslink RPC whose handler takes its typed params and returns its typed response.

    The RPC is still callable with a plain dict (as wslink and other protocols do)
    and returns a plain dict.
    """
    rpc_id = prefix + route.schema["rpc"]
    validate_response = fastjsonschema.compile(route.schema["response"])

    def decorator(
        handler: Callable[[SelfT, ParamsT], ResponseT],
    ) -> Callable[Concatenate[SelfT, ...], dict[str, Any]]:
        @functools.wraps(handler)
        def rpc(
            self: SelfT, rpc_params: RpcParams | None = None, **kwargs: object
        ) -> dict[str, Any]:
            do_stream = bool(kwargs.pop("stream", False))
            json_data = rpc_params if rpc_params is not None else {}
            validate_schema(json_data, route.schema, prefix)
            result = handler(self, route.params.from_dict(json_data))
            if not isinstance(result, route.response):
                msg = (
                    f"{handler.__name__} returned {type(result).__name__}, "
                    f"expected {route.response.__name__}"
                )
                raise TypeError(msg)
            payload = _to_payload(result)
            if _validate_responses():
                validate_response(payload)
            if do_stream:
                self.publish(rpc_id, rpc_params)
            return payload

        setattr(rpc, TYPED_RPC_MARKER, True)
        return register(rpc_id)(rpc)  # type: ignore[no-any-return]

    return decorator
