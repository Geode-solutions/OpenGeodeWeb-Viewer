# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.edges.mesh_edges_protocols import VtkMeshEdgesView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor


def test_edges_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image("mesh/edges/visibility.jpeg") == True


def test_edges_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_edges_visibility(server, dataset_factory)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/edges/color.jpeg") == True


def test_edges_with_edged_curve(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(
        id="123456789", viewable_file="edged_curve.vtp", viewer_elements_type="edges"
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("mesh/edges/register_edged_curve.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/edges/edged_curve_color.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("mesh/edges/edged_curve_visibility.jpeg") == True


def test_edges_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )
    assert server.compare_image("mesh/edges/vertex_attribute.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/edges/vertex_scalar_range.jpeg") == True


def test_edges_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Set scalar range
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 58}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg") == True


def test_edges_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg") == True

    # Set scalar range: 50 to 58 (clamping data to the minimum color -> mostly BLUE)
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 50.0, "maximum": 58.0}],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_range_update.jpeg") == True


def test_edges_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg") == True

    # Set scalar range: 0.0 to 1.0 (all data > 1.0 should become RED)
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0.0, "maximum": 1.0}],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_red_shift.jpeg") == True


def test_edges_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 71, 71, 219],
                    [0.143, 0, 0, 92],
                    [0.285, 0, 255, 255],
                    [0.429, 0, 128, 0],
                    [0.571, 255, 255, 0],
                    [0.714, 255, 97, 0],
                    [0.857, 107, 0, 0],
                    [1.0, 224, 77, 77],
                ],
            }
        ],
    )

    assert (
        server.compare_image("mesh/edges/vertex_color_map_rainbow_initial.jpeg") == True
    )

    # Set scalar range
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 10.0, "maximum": 20.0}],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_rainbow.jpeg") == True
