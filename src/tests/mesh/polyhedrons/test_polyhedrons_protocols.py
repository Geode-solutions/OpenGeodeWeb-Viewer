# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polyhedrons.polyhedrons_protocols import VtkMeshPolyhedronsView

# Local application imports


def test_register_mesh(server):

    server.call(VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "hybrid_solid.vtu"}])
    assert server.compare_image(3, "mesh/polyhedrons/register.jpeg") == True

def test_polyhedrons_color(server):

    test_register_mesh(server)

    server.call(VtkMeshPolyhedronsView.mesh_polyhedrons_prefix + VtkMeshPolyhedronsView.mesh_polyhedrons_schemas_dict["color"]["rpc"], [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}])
    assert server.compare_image(3, "mesh/polyhedrons/color.jpeg") == True