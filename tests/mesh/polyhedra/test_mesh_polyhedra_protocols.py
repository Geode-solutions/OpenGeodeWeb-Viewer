# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polyhedra.polyhedra_protocols import (
    VtkMeshPolyhedraView,
)

# Local application imports
from tests.conftest import ServerMonitor


def test_register_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(
        id="123456789",
        viewable_file="polyhedron_attribute.vtu",
        viewer_elements_type="polyhedra",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("mesh/polyhedra/register.jpeg") == True


def test_polyhedra_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/polyhedra/color.jpeg") == True


def test_polyhedra_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("mesh/polyhedra/visibility.jpeg") == True


def test_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )
    assert server.compare_image("mesh/polyhedra/vertex_attribute.jpeg") == True

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/polyhedra/vertex_scalar_range.jpeg") == True


def test_polyhedron_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )
    assert server.compare_image("mesh/polyhedra/polyhedron_attribute.jpeg") == True

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/polyhedra/polyhedron_scalar_range.jpeg") == True


def test_polyhedra_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )

    # Set scalar range
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 0, "maximum": 1}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True


def test_polyhedra_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True

    # Set scalar range: 10 to 11 (clamping data to the minimum color -> mostly BLUE)
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 10.0, "maximum": 11.0}],
    )

    assert (
        server.compare_image("mesh/polyhedra/vertex_color_map_range_update.jpeg")
        == True
    )


def test_polyhedra_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True

    # Set scalar range: 0.0 to 1.0 (all data > 1.0 should become RED)
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 0.0, "maximum": 1.0}],
    )

    assert (
        server.compare_image("mesh/polyhedra/vertex_color_map_red_shift.jpeg") == True
    )


def test_polyhedra_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
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
        server.compare_image("mesh/polyhedra/vertex_color_map_rainbow_initial.jpeg")
        == True
    )

    # Set scalar range: 2.0 to 8.0
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 2.0, "maximum": 8.0}],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map_rainbow.jpeg") == True


def test_polyhedra_polyhedron_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )

    # Set scalar range
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 0, "maximum": 1}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/polyhedron_color_map.jpeg") == True


def test_polyhedra_polyhedron_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/polyhedron_color_map.jpeg") == True

    # Set scalar range: 5 to 6 (clamping data to the minimum color -> mostly BLUE)
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 5.0, "maximum": 6.0}],
    )

    assert (
        server.compare_image("mesh/polyhedra/polyhedron_color_map_range_update.jpeg")
        == True
    )


def test_polyhedra_polyhedron_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/polyhedron_color_map.jpeg") == True

    # Set scalar range: 0.0 to 1.0 (all data > 1 should become RED)
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 0.0, "maximum": 1.0}],
    )

    assert (
        server.compare_image("mesh/polyhedra/polyhedron_color_map_red_shift.jpeg")
        == True
    )


def test_polyhedra_polyhedron_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
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
        server.compare_image("mesh/polyhedra/polyhedron_color_map_rainbow_initial.jpeg")
        == True
    )

    # Set scalar range: 3.5 to 5.5
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 3.5, "maximum": 5.5}],
    )

    assert (
        server.compare_image("mesh/polyhedra/polyhedron_color_map_rainbow.jpeg") == True
    )
