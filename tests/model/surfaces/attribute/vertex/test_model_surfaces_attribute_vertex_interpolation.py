# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.attribute.vertex.surfaces_attribute_vertex_protocols import (
    VtkModelSurfacesAttributeVertexView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
model_id = "12345678901234567890123456789012"
surface_ids = [18, 19, 20]


def test_surfaces_vertex_attribute_interpolates_through_colormap(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    # Regression test for a bug where the color of a point-attribute-colored
    # surface was interpolated by blending per-vertex colors linearly in RGB
    # space instead of interpolating the scalar and mapping it through the
    # colormap. With a colormap that has a light color in the middle of the
    # range, the buggy behavior never shows that light color between two
    # differently colored vertices.
    dataset_factory(id=model_id, viewable_file="implicit_attribute.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": model_id, "name": "implicit_attribute.vtm"}],
    )

    # Hide everything to ensure visibility of the surfaces only
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 21)), "visibility": False}],
    )
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": surface_ids, "visibility": True}],
    )

    # "geode_implicit_attribute" is the real point attribute from the
    # reported bug, ranging roughly from -1.67 to 6.79 on this dataset.
    server.call(
        VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_prefix
        + VtkModelSurfacesAttributeVertexView.model_surfaces_attribute_vertex_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": surface_ids,
                "name": "geode_implicit_attribute",
                "item": 0,
                "points": [
                    -2.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    -2.0 + 0.143 * 9.0,
                    0,
                    0,
                    92 / 255,
                    -2.0 + 0.285 * 9.0,
                    0,
                    255 / 255,
                    255 / 255,
                    -2.0 + 0.429 * 9.0,
                    0,
                    128 / 255,
                    0,
                    -2.0 + 0.571 * 9.0,
                    255 / 255,
                    255 / 255,
                    0,
                    -2.0 + 0.714 * 9.0,
                    255 / 255,
                    97 / 255,
                    0,
                    -2.0 + 0.857 * 9.0,
                    107 / 255,
                    0,
                    0,
                    7.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": -2.0,
                "maximum": 7.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert (
        server.compare_image("model/surfaces/implicit_attribute_color_map.jpeg")
        == True
    )
