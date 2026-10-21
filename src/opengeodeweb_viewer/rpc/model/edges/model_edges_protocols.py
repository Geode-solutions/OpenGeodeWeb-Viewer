# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelEdgesView(VtkModelView):
    model_edges_prefix = "opengeodeweb_viewer.model.edges."
    model_edges_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_edges_prefix, schemas.visibility_route)
    def set_model_edges_visibility(self, params: schemas.Visibility) -> schemas.VisibilityResponse:
        self.set_model_edges_visibility_on_all(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(model_edges_prefix, schemas.width_route)
    def set_model_edges_width(self, params: schemas.Width) -> schemas.WidthResponse:
        self.set_model_edges_width_on_all(params.id, params.width)
        return schemas.WidthResponse()
