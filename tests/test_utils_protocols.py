from typing import TYPE_CHECKING

from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.utils_protocols import VtkUtilsView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.conftest import ServerMonitor


def test_reset_project_after_import(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    # Mock
    pre_id = "00000000000000000000000123456789"
    dataset_factory(data_id=pre_id, viewable_file="hat.vtp", viewer_elements_type="polygons")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": pre_id, "name": "hat.vtp"}],
    )
    assert server.compare_image("mesh/register.jpeg") is True

    # Import
    with get_session() as session:
        session.query(Data).delete()
        session.commit()

    post_id = "00000000000000000000000987654321"
    dataset_factory(data_id=post_id, viewable_file="hat.vtp", viewer_elements_type="polygons")

    server.call(
        VtkUtilsView.utils_prefix + VtkUtilsView.utils_schemas_dict["import_project"]["rpc"]
    )
    server.get_result(
        VtkUtilsView.utils_prefix + VtkUtilsView.utils_schemas_dict["import_project"]["rpc"]
    )

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    assert server.compare_image("viewer/reset_visualization.jpeg") is True

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": post_id, "name": "hat.vtp"}],
    )
    assert server.compare_image("viewer/import_project.jpeg") is True


def test_scene_style_after_import(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    server.call(
        VtkUtilsView.utils_prefix + VtkUtilsView.utils_schemas_dict["import_project"]["rpc"]
    )
    server.get_result(
        VtkUtilsView.utils_prefix + VtkUtilsView.utils_schemas_dict["import_project"]["rpc"]
    )
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_text_style"]["rpc"],
        [{"color": {"r": 255, "g": 0, "b": 0}, "font_family": "arial", "opacity": 1.0}],
    )
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_orientation_widget"]["rpc"],
        [{"marker": "compass"}],
    )
    assert server.compare_image("viewer/orientation_widget_compass.jpeg") is True
