# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.surfaces.polygons.surfaces_polygons_protocols import (
    VtkModelSurfacesPolygonsView,
)

# Local application imports


def test_register_model(server):

    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "cube.vtm"}],
    )
    assert server.compare_image(3, "model/cube_register.jpeg") == True


def test_surfaces_polygons_visibility(server):

    test_register_model(server)

    server.call(
        VtkModelSurfacesPolygonsView.model_surfaces_polygons_prefix
        + VtkModelSurfacesPolygonsView.model_surfaces_polygons_schemas_dict[
            "visibility"
        ]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": ["32", "33", "34", "35", "36", "37", "38", "39", "40"],
                "visibility": True,
            }
        ],
    )
    assert server.compare_image(3, "model/surfaces/polygons/visibility.jpeg") == True
