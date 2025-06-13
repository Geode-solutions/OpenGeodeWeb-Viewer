# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.edges.model_edges_protocols import (
    VtkModelEdgesView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model


def test_edges_visibility(server):

    test_register_model(server)

    server.call(
        VtkModelEdgesView.model_edges_prefix
        + VtkModelEdgesView.model_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image(3, "model/edges/visibility.jpeg") == True
