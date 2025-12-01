# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polygons.polygons_protocols import VtkMeshPolygonsView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor


def test_polygons_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/polygons/color.jpeg") == True


def test_polygons_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("mesh/polygons/visibility.jpeg") == True


def test_polygons_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "lambert2SG"}],
    )
    assert server.compare_image("mesh/polygons/vertex_attribute.jpeg") == True

def test_polygons_polygon_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id="123456789", viewable_file="triangulated_surface2d.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("mesh/polygons/register.jpeg") == True

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_attribute"]["rpc"],
        [{"id": "123456789", "name": "triangle_vertices"}],
    )
    assert server.compare_image("mesh/polygons/polygon_attribute.jpeg") == True
