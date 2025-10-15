from typing import Callable
from opengeodeweb_viewer.rpc.generic.generic_protocols import VtkGenericView
from tests.conftest import ServerMonitor


def test_register_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    data_id = "123456789"
    dataset_factory(id=data_id, viewable_file_name="hat.vtp")

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [{"id": data_id}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") is True


def test_register_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    data_id = "123456789"
    dataset_factory(id=data_id, viewable_file_name="CrossSection.vtm")

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [{"id": data_id}],
    )
    assert server.compare_image(3, "model/register.jpeg") is True


def test_deregister_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "mesh/deregister.jpeg") == True


def test_deregister_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_model(server, dataset_factory)

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/deregister.jpeg") == True
