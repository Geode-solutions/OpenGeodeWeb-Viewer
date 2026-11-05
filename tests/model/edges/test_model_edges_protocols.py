# Standard library imports

# Third party imports
from typing import TYPE_CHECKING

from opengeodeweb_viewer.rpc.model.blocks.edges.model_blocks_edges_protocols import (
    VtkModelBlocksEdgesView,
)
from opengeodeweb_viewer.rpc.model.edges.model_edges_protocols import (
    VtkModelEdgesView,
)
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.surfaces.edges.attribute.vertex import (
    surfaces_edges_attribute_vertex_protocols,
)
from opengeodeweb_viewer.rpc.model.surfaces.edges.model_surfaces_edges_protocols import (
    VtkModelSurfacesEdgesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.model.test_model_protocols import (
    test_model_cube_side_view,
    test_register_model,
    test_register_model_cube,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.conftest import ServerMonitor

VtkModelSurfacesEdgesAttributeVertexView = (
    surfaces_edges_attribute_vertex_protocols.VtkModelSurfacesEdgesAttributeVertexView
)

# Local constants
model_id = "12345678901234567890123456789012"
surfaces_ids = list(range(36, 47))
blocks_ids = list(range(48, 50))


def test_edges_visibility(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelEdgesView.model_edges_prefix
        + VtkModelEdgesView.model_edges_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "visibility": True}],
    )
    assert server.compare_image("model/edges/visibility.jpeg")


def test_edges_width(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_edges_visibility(server, dataset_factory)

    server.call(
        VtkModelEdgesView.model_edges_prefix
        + VtkModelEdgesView.model_edges_schemas_dict["width"]["rpc"],
        [{"id": model_id, "width": 6}],
    )
    assert server.compare_image("model/edges/width.jpeg")


def call_surfaces_edges(server: ServerMonitor, route: str, params: dict[str, object]) -> None:
    view = VtkModelSurfacesEdgesView
    server.call(
        view.model_surfaces_edges_prefix + view.model_surfaces_edges_schemas_dict[route]["rpc"],
        [{"id": model_id, **params}],
    )


def test_surfaces_edges_color(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_model_cube_side_view(server, dataset_factory)
    call_surfaces_edges(server, "visibility", {"block_ids": surfaces_ids, "visibility": True})
    call_surfaces_edges(server, "width", {"block_ids": surfaces_ids, "width": 3})
    call_surfaces_edges(
        server,
        "color",
        {"block_ids": surfaces_ids, "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0}},
    )
    assert server.compare_image("model/edges/surfaces_edges_color.jpeg")


def test_surface_edges_width(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_surfaces_edges_color(server, dataset_factory)
    call_surfaces_edges(server, "width", {"block_ids": [45], "width": 8})
    assert server.compare_image("model/edges/surface_edges_width.jpeg")


def test_surfaces_edges_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surfaces_edges_color(server, dataset_factory)
    view = VtkModelSurfacesEdgesAttributeVertexView
    server.call(
        view.model_surfaces_edges_attribute_vertex_prefix
        + view.model_surfaces_edges_attribute_vertex_schemas_dict["attribute"]["rpc"],
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
    assert server.compare_image("model/edges/surfaces_edges_attribute.jpeg")


def test_surfaces_edges_attribute_model_hidden_then_shown(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surfaces_edges_attribute(server, dataset_factory)
    for visibility in (False, True):
        server.call(
            VtkModelView.model_prefix + VtkModelView.model_schemas_dict["visibility"]["rpc"],
            [{"id": model_id, "visibility": visibility}],
        )
    # The edges scalar bar comes back with the model
    assert server.compare_image("model/edges/surfaces_edges_attribute.jpeg")


def test_surfaces_edges_opacity(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_surfaces_edges_color(server, dataset_factory)
    call_surfaces_edges(
        server,
        "color",
        {"block_ids": surfaces_ids, "color": {"red": 255, "green": 0, "blue": 0, "alpha": 0.2}},
    )
    assert server.compare_image("model/edges/surfaces_edges_opacity.jpeg")


def test_surfaces_edges_hidden_blocks(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surfaces_edges_color(server, dataset_factory)
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": surfaces_ids, "visibility": False}],
    )
    # Hidden surfaces take their edges with them
    assert server.compare_image("model/edges/surfaces_edges_hidden_blocks.jpeg")


def test_surfaces_edges_explode(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_surfaces_edges_color(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["explode"]["rpc"],
        [{"ids": [model_id], "explode_factor": 1.0}],
    )
    assert server.compare_image("model/edges/surfaces_edges_explode.jpeg")


def test_surfaces_edges_behind_surface(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)
    call_surfaces_edges(server, "visibility", {"block_ids": surfaces_ids, "visibility": True})
    call_surfaces_edges(server, "width", {"block_ids": surfaces_ids, "width": 4})
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": {
                    "focal_point": [5.0, 0.0, 5.0],
                    "view_up": [0.0, 0.0, 1.0],
                    "position": [5.0, -6.0, 13.0],
                    "view_angle": 30.0,
                    "clipping_range": [0.5, 30.0],
                }
            }
        ],
    )
    # Grazing view of a face: the edges of the surfaces behind it stay hidden
    assert server.compare_image("model/edges/surfaces_edges_behind_surface.jpeg")


def test_model_edges_width_after_component_width(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_surface_edges_width(server, dataset_factory)
    server.call(
        VtkModelEdgesView.model_edges_prefix
        + VtkModelEdgesView.model_edges_schemas_dict["width"]["rpc"],
        [{"id": model_id, "width": 1}],
    )
    # Model width overrides every component width, block 45 included
    assert server.compare_image("model/edges/width_after_component_width.jpeg")


def test_blocks_edges_color(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_model_cube_side_view(server, dataset_factory)
    view = VtkModelBlocksEdgesView
    for route, params in (
        ("visibility", {"visibility": True}),
        ("color", {"color": {"red": 0, "green": 0, "blue": 255, "alpha": 1.0}}),
    ):
        server.call(
            view.model_blocks_edges_prefix + view.model_blocks_edges_schemas_dict[route]["rpc"],
            [{"id": model_id, "block_ids": blocks_ids, **params}],
        )
    assert server.compare_image("model/edges/blocks_edges_color.jpeg")
