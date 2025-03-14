# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polyhedrons.polyhedrons_protocols import (
    VtkMeshPolyhedronsView,
)

# Local application imports


def test_register_mesh(server):

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "hybrid_solid.vtu"}],
    )
    assert server.compare_image(3, "mesh/polyhedrons/register.jpeg") == True


def test_polyhedrons_color(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPolyhedronsView.mesh_polyhedrons_prefix
        + VtkMeshPolyhedronsView.mesh_polyhedrons_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/polyhedrons/color.jpeg") == True


def test_polyhedrons_visibility(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPolyhedronsView.mesh_polyhedrons_prefix
        + VtkMeshPolyhedronsView.mesh_polyhedrons_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "mesh/polyhedrons/visibility.jpeg") == True


def test_vertex_attribute(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPolyhedronsView.mesh_polyhedrons_prefix
        + VtkMeshPolyhedronsView.mesh_polyhedrons_schemas_dict["vertex_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )
    assert server.compare_image(3, "mesh/polyhedrons/vertex_attribute.jpeg") == True


def test_polyhedron_attribute(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPolyhedronsView.mesh_polyhedrons_prefix
        + VtkMeshPolyhedronsView.mesh_polyhedrons_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )
    assert server.compare_image(3, "mesh/polyhedrons/polyhedron_attribute.jpeg") == True
