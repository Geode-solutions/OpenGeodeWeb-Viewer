# Standard library imports
from collections.abc import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.blocks.edges.model_blocks_edges_protocols import (
    VtkModelBlocksEdgesView,
)
from opengeodeweb_viewer.rpc.model.edges.model_edges_protocols import (
    VtkModelEdgesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.edges.model_surfaces_edges_protocols import (
    VtkModelSurfacesEdgesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from tests.conftest import ServerMonitor

# Local application imports
from tests.model.test_model_protocols import test_model_cube_side_view, test_register_model

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
