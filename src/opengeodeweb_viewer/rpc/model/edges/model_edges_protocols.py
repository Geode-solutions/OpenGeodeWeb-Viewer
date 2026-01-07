# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelEdgesView(VtkModelView):
    model_edges_prefix = "opengeodeweb_viewer.model.edges."
    model_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_edges_prefix + model_edges_schemas_dict["visibility"]["rpc"])
    def setModelEdgesVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_edges_schemas_dict["visibility"],
            self.model_edges_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetEdgesVisibility(params.id, params.visibility)
