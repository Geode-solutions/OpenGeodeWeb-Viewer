# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkModelEdgesView(VtkModelView):
    model_edges_prefix = "opengeodeweb_viewer.model.edges."
    model_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_edges_prefix, schemas.visibility_route)
    def setModelEdgesVisibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.SetEdgesVisibility(params.id, params.visibility)
        return schemas.VisibilityResponse()
