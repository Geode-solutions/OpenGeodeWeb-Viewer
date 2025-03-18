# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.surfaces.polygons.surfaces_polygons_protocols import (
    VtkModelSurfacesPolygonsView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model_cube


def test_surfaces_polygons_visibility(server):

    test_register_model_cube(server)
    server.call(
        VtkModelSurfacesPolygonsView.model_surfaces_polygons_prefix
        + VtkModelSurfacesPolygonsView.model_surfaces_polygons_schemas_dict[
            "visibility"
        ]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(36, 49)),
                "visibility": False,
            }
        ],
    )

    assert server.compare_image(3, "model/surfaces/polygons/visibility.jpeg") == True
