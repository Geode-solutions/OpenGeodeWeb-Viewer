# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.attribute.vertex.surfaces_attribute_vertex_protocols import (
    VtkModelSurfacesAttributeVertexView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor

model_id = "123456789"


def test_surfaces_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    server.call(
        VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_prefix
        + VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "name": "unique vertices"}],
    )
    assert (
        server.compare_image("model/surfaces/vertex_attribute.jpeg") == True
    )


def test_surfaces_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    # Set active vertex attribute
    server.call(
        VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_prefix
        + VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "name": "unique vertices"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_prefix
        + VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert (
        server.compare_image("model/surfaces/vertex_color_map.jpeg") == True
    )
