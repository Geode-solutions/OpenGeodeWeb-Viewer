# Standard library imports
from collections.abc import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.lines.points.model_lines_points_protocols import (
    VtkModelLinesPointsView,
)
from opengeodeweb_viewer.rpc.model.points.model_points_protocols import (
    VtkModelPointsView,
)
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.points.attribute.vertex import (
    surfaces_points_attribute_vertex_protocols,
)
from opengeodeweb_viewer.rpc.model.surfaces.points.model_surfaces_points_protocols import (
    VtkModelSurfacesPointsView,
)
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from tests.conftest import ServerMonitor

# Local application imports
from tests.model.test_model_protocols import test_model_cube_side_view, test_register_model

VtkModelSurfacesPointsAttributeVertexView = (
    surfaces_points_attribute_vertex_protocols.VtkModelSurfacesPointsAttributeVertexView
)

# Local constants
model_id = "12345678901234567890123456789012"
surfaces_ids = list(range(36, 47))
lines_ids = list(range(15, 35))


def test_points_visibility(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelPointsView.model_points_prefix
        + VtkModelPointsView.model_points_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "visibility": True}],
    )
    assert server.compare_image("model/points/visibility.jpeg")


def test_points_size(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_points_visibility(server, dataset_factory)

    server.call(
        VtkModelPointsView.model_points_prefix
        + VtkModelPointsView.model_points_schemas_dict["size"]["rpc"],
        [{"id": model_id, "size": 20}],
    )
    assert server.compare_image("model/points/size.jpeg")


def test_surfaces_points_color(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_model_cube_side_view(server, dataset_factory)

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": surfaces_ids, "visibility": True}],
    )
    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["size"]["rpc"],
        [{"id": model_id, "block_ids": surfaces_ids, "size": 8}],
    )
    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["color"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": surfaces_ids,
                "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("model/points/surfaces_points_color.jpeg")


def test_lines_points_size(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_surfaces_points_color(server, dataset_factory)

    server.call(
        VtkModelLinesPointsView.model_lines_points_prefix
        + VtkModelLinesPointsView.model_lines_points_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": lines_ids, "visibility": True}],
    )
    server.call(
        VtkModelLinesPointsView.model_lines_points_prefix
        + VtkModelLinesPointsView.model_lines_points_schemas_dict["size"]["rpc"],
        [{"id": model_id, "block_ids": lines_ids, "size": 14}],
    )
    server.call(
        VtkModelLinesPointsView.model_lines_points_prefix
        + VtkModelLinesPointsView.model_lines_points_schemas_dict["color"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": lines_ids,
                "color": {"red": 0, "green": 0, "blue": 255, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("model/points/lines_points_size.jpeg")


def test_surfaces_points_hidden_blocks(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_lines_points_size(server, dataset_factory)

    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": surfaces_ids, "visibility": False}],
    )
    assert server.compare_image("model/points/surfaces_points_hidden_blocks.jpeg")


def test_surfaces_points_explode(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surfaces_points_color(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["explode"]["rpc"],
        [{"ids": [model_id], "explode_factor": 1.0}],
    )
    assert server.compare_image("model/points/surfaces_points_explode.jpeg")


def test_surface_points_size(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_surfaces_points_color(server, dataset_factory)

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["size"]["rpc"],
        [{"id": model_id, "block_ids": [45], "size": 20}],
    )
    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["color"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": [45],
                "color": {"red": 0, "green": 255, "blue": 0, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("model/points/surface_points_size.jpeg")


def test_surfaces_points_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surfaces_points_color(server, dataset_factory)

    attribute_view = VtkModelSurfacesPointsAttributeVertexView
    server.call(
        attribute_view.model_surfaces_points_attribute_vertex_prefix
        + attribute_view.model_surfaces_points_attribute_vertex_schemas_dict["attribute"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": surfaces_ids,
                "name": "unique vertices",
                "item": 0,
                "points": [0.0, 0.0, 0.0, 1.0, 663.0, 1.0, 0.0, 0.0],
                "minimum": 0.0,
                "maximum": 663.0,
            }
        ],
    )
    assert server.compare_image("model/points/surfaces_points_attribute.jpeg")


def test_surfaces_points_opacity(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surfaces_points_color(server, dataset_factory)

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["color"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": surfaces_ids,
                "color": {"red": 255, "green": 0, "blue": 0, "alpha": 0.2},
            }
        ],
    )
    assert server.compare_image("model/points/surfaces_points_opacity.jpeg")
