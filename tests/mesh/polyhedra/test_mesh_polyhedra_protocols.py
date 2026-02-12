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
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 1, "maximum": 11}],
    )
    assert server.compare_image("mesh/polyhedra/vertex_attribute.jpeg") == True


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
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"][
            "rpc"
        ],
        [{"id": "123456789", "minimum": 3, "maximum": 6}],
    )
    assert server.compare_image("mesh/polyhedra/polyhedron_attribute.jpeg") == True


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

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    1.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
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
                    1.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    10.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 10.0,
                "maximum": 11.0,
            }
        ],
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

    # Set Blue to Red Map on [1, 11]
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    1.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
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
                    1.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    1.0 + 0.143 * 10,
                    0,
                    0,
                    92 / 255,
                    1.0 + 0.285 * 10,
                    0,
                    255 / 255,
                    255 / 255,
                    1.0 + 0.429 * 10,
                    0,
                    128 / 255,
                    0,
                    1.0 + 0.571 * 10,
                    255 / 255,
                    255 / 255,
                    0,
                    1.0 + 0.714 * 10,
                    255 / 255,
                    97 / 255,
                    0,
                    1.0 + 0.857 * 10,
                    107 / 255,
                    0,
                    0,
                    11.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polyhedra/vertex_color_map_rainbow_initial.jpeg")
        == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    2.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    2.0 + 0.143 * 6,
                    0,
                    0,
                    92 / 255,
                    2.0 + 0.285 * 6,
                    0,
                    255 / 255,
                    255 / 255,
                    2.0 + 0.429 * 6,
                    0,
                    128 / 255,
                    0,
                    2.0 + 0.571 * 6,
                    255 / 255,
                    255 / 255,
                    0,
                    2.0 + 0.714 * 6,
                    255 / 255,
                    97 / 255,
                    0,
                    2.0 + 0.857 * 6,
                    107 / 255,
                    0,
                    0,
                    8.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 2.0,
                "maximum": 8.0,
            }
        ],
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
                    3.0,
                    0,
                    0,
                    1.0,
                    6.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 3.0,
                "maximum": 6.0,
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
                    3.0,
                    0,
                    0,
                    1.0,
                    6.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 3.0,
                "maximum": 6.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/polyhedron_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    5.0,
                    0,
                    0,
                    1.0,
                    6.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 5.0,
                "maximum": 6.0,
            }
        ],
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

    # Set Blue to Red Map on [3, 6]
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    3.0,
                    0,
                    0,
                    1.0,
                    6.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 3.0,
                "maximum": 6.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/polyhedron_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
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
                    3.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    3.0 + 0.143 * 3,
                    0,
                    0,
                    92 / 255,
                    3.0 + 0.285 * 3,
                    0,
                    255 / 255,
                    255 / 255,
                    3.0 + 0.429 * 3,
                    0,
                    128 / 255,
                    0,
                    3.0 + 0.571 * 3,
                    255 / 255,
                    255 / 255,
                    0,
                    3.0 + 0.714 * 3,
                    255 / 255,
                    97 / 255,
                    0,
                    3.0 + 0.857 * 3,
                    107 / 255,
                    0,
                    0,
                    6.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 3.0,
                "maximum": 6.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polyhedra/polyhedron_color_map_rainbow_initial.jpeg")
        == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedra_color_map"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "points": [
                    3.5,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    3.5 + 0.143 * 2,
                    0,
                    0,
                    92 / 255,
                    3.5 + 0.285 * 2,
                    0,
                    255 / 255,
                    255 / 255,
                    3.5 + 0.429 * 2,
                    0,
                    128 / 255,
                    0,
                    3.5 + 0.571 * 2,
                    255 / 255,
                    255 / 255,
                    0,
                    3.5 + 0.714 * 2,
                    255 / 255,
                    97 / 255,
                    0,
                    3.5 + 0.857 * 2,
                    107 / 255,
                    0,
                    0,
                    5.5,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 3.5,
                "maximum": 5.5,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polyhedra/polyhedron_color_map_rainbow.jpeg") == True
    )
