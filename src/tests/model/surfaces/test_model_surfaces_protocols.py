# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.surfaces.surfaces_protocols import (
    VtkModelSurfacesView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model_cube


def test_surfaces_polygons_visibility(server):

    test_register_model_cube(server)

    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(1, 50)),
                "visibility": False,
            }
        ],
    )
    assert server.compare_image(3, "model/cube_visibility_false.jpeg") == True

    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(36, 49)),
                "visibility": True,
            }
        ],
    )

    assert server.compare_image(3, "model/surfaces/visibility.jpeg") == True


def test_surfaces_polygons_color(server):

    test_surfaces_polygons_visibility(server)

    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(36, 49)),
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image(3, "model/surfaces/color.jpeg") == True
