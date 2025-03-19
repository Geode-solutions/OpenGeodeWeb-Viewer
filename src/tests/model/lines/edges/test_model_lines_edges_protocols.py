# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.lines.edges.lines_edges_protocols import (
    VtkModelLinesEdgesView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model_cube


def test_lines_edges_visibility(server):

    test_register_model_cube(server)

    server.call(
        VtkModelLinesEdgesView.model_lines_edges_prefix
        + VtkModelLinesEdgesView.model_lines_edges_schemas_dict["visibility"]["rpc"],
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
        VtkModelLinesEdgesView.model_lines_edges_prefix
        + VtkModelLinesEdgesView.model_lines_edges_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(14, 35)),
                "visibility": True,
            }
        ],
    )
    assert server.compare_image(3, "model/lines/edges/visibility.jpeg") == True


def test_lines_edges_color(server):

    test_lines_edges_visibility(server)

    server.call(
        VtkModelLinesEdgesView.model_lines_edges_prefix
        + VtkModelLinesEdgesView.model_lines_edges_schemas_dict["color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(14, 35)),
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image(3, "model/lines/edges/color.jpeg") == True
