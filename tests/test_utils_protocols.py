from typing import Callable
from opengeodeweb_viewer.rpc.utils_protocols import VtkUtilsView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data
from tests.conftest import ServerMonitor


def test_reset_project_after_import(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    # Mock
    pre_id = "123456789"
    dataset_factory(id=pre_id, viewable_file="hat.vtp")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": pre_id}],
    )
    assert server.compare_image("mesh/register.jpeg") is True

    # Import
    with get_session() as session:
        session.query(Data).delete()
        session.commit()

    post_id = "987654321"
    dataset_factory(id=post_id, viewable_file="hat.vtp")

    server.call(
        VtkUtilsView.utils_prefix
        + VtkUtilsView.utils_schemas_dict["import_project"]["rpc"]
    )
    server.get_response()

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    assert server.compare_image("viewer/reset_visualization.jpeg") is True

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": post_id}],
    )
    assert server.compare_image("viewer/import_project.jpeg") is True
