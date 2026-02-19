# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polyhedra.attribute.polyhedron.polyhedra_attribute_polyhedron_protocols import (
    VtkMeshPolyhedraAttributePolyhedronView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id,
        viewable_file="polyhedron_attribute.vtu",
        viewer_elements_type="polyhedra",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )



def test_polyhedra_polyhedron_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_polyhedra"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_polyhedra"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_polyhedra"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_polyhedra"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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
        VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_prefix
        + VtkMeshPolyhedraAttributePolyhedronView.mesh_polyhedra_attribute_polyhedron_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
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
