# Standard library imports
import importlib
import inspect
import pkgutil
from typing import Any

# Third party imports
import fastjsonschema  # type: ignore
import pytest

# Local application imports
from opengeodeweb_viewer import rpc
from opengeodeweb_viewer.typed_rpc import TYPED_RPC_MARKER, typed_rpc
from opengeodeweb_viewer.rpc.viewer import schemas

PREFIX = "opengeodeweb_viewer."


def _registered_rpcs() -> dict[str, Any]:
    rpcs: dict[str, Any] = {}
    for module_info in pkgutil.walk_packages(rpc.__path__, rpc.__name__ + "."):
        if not module_info.name.endswith("_protocols"):
            continue
        module = importlib.import_module(module_info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            for _, function in inspect.getmembers(cls, inspect.isfunction):
                for uri in getattr(function, "_wslinkuris", []):
                    rpcs[uri["uri"]] = function
    return rpcs


def test_every_rpc_is_typed() -> None:
    rpcs = {uri: f for uri, f in _registered_rpcs().items() if uri.startswith(PREFIX)}
    assert rpcs
    for uri, function in rpcs.items():
        assert getattr(
            function, TYPED_RPC_MARKER, False
        ), f"{uri} must be registered with @typed_rpc"


class _Protocol:
    def __init__(self) -> None:
        self.published: list[tuple[str, Any]] = []

    def publish(self, rpc_id: str, params: Any) -> None:
        self.published.append((rpc_id, params))

    @typed_rpc(PREFIX, schemas.pick_colormap_route)
    def pick(self, params: schemas.PickColormap) -> schemas.PickColormapResponse:
        return schemas.PickColormapResponse(data_id=None)

    @typed_rpc(PREFIX, schemas.get_point_position_route)
    def wrong_type(
        self, params: schemas.GetPointPosition
    ) -> schemas.GetPointPositionResponse:
        return schemas.PickColormapResponse()  # type: ignore[return-value]

    @typed_rpc(PREFIX, schemas.get_point_position_route)
    def invalid_payload(
        self, params: schemas.GetPointPosition
    ) -> schemas.GetPointPositionResponse:
        return schemas.GetPointPositionResponse(x="a", y=0, z=0)  # type: ignore[arg-type]


def test_typed_rpc_returns_dict_without_none() -> None:
    assert _Protocol().pick({"x": 1, "y": 2}) == {}


def test_typed_rpc_stream_publishes() -> None:
    protocol = _Protocol()
    protocol.pick({"x": 1, "y": 2}, stream=True)
    assert protocol.published == [(PREFIX + "pick_colormap", {"x": 1, "y": 2})]


def test_typed_rpc_bad_params() -> None:
    with pytest.raises(Exception, match="Bad request"):
        _Protocol().pick({"x": "not a number", "y": 2})


def test_typed_rpc_wrong_response_type() -> None:
    with pytest.raises(TypeError):
        _Protocol().wrong_type({"x": 1, "y": 2})


def test_typed_rpc_invalid_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHON_ENV", "test")
    with pytest.raises(fastjsonschema.JsonSchemaException):
        _Protocol().invalid_payload({"x": 1, "y": 2})
