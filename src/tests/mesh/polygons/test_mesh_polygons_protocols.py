# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.mesh.polygons.polygons_protocols import VtkMeshPolygonsView

# Local application imports
from src.tests.mesh.test_mesh_protocols import test_register_mesh


def test_polygons_color(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/polygons/color.jpeg") == True


def test_polygons_visibility(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "mesh/polygons/visibility.jpeg") == True
