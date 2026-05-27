from typing import Callable
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from tests.conftest import ServerMonitor


def test_register_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id="123456789", viewable_file="CrossSection.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "name": "test_name"}],
    )
    assert server.compare_image("model/register.jpeg") == True


def test_register_model_cube(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id="123456789", viewable_file="cube.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "name": "test_name"}],
    )
    assert server.compare_image("model/cube_register.jpeg") == True


def test_visibility_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("model/visibility.jpeg") == True


def test_deregister_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("model/deregister.jpeg") == True


def test_get_blocks_bounds(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    rpc = VtkModelView.model_prefix + "get_blocks_bounds"
    server.call(rpc, [{"id": "123456789", "block_ids": [2]}])

    response = server.get_response()
    while isinstance(response, bytes) or response.get("id") != f"rpc:{rpc}":
        response = server.get_response()

    assert response.get("result") == [4.9, 4.9, 3.1, 3.1, 0.0, 0.0]
