# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.mesh.edges.edges_protocols import VtkMeshEdgesView

# Local application imports
from tests.test_mesh_protocols import test_register_mesh

def test_edges_visibility(server):

    test_register_mesh(server)

    server.call(VtkMeshEdgesView.mesh_edges_prefix + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"], [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "mesh/edges/visibility.jpeg") == True

def test_edges_color(server):

    test_edges_visibility(server)

    server.call(VtkMeshEdgesView.mesh_edges_prefix + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"], [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}])
    assert server.compare_image(3, "mesh/edges/color.jpeg") == True
