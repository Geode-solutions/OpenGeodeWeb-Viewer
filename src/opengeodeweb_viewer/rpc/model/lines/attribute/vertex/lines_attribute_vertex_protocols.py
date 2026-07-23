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


class VtkModelLinesAttributeVertexView(VtkModelView):
    model_lines_attribute_vertex_prefix = (
        "opengeodeweb_viewer.model.lines.attribute.vertex."
    )
    model_lines_attribute_vertex_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(
        model_lines_attribute_vertex_prefix
        + model_lines_attribute_vertex_schemas_dict["attribute"]["rpc"]
    )
    def setModelLinesVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_lines_attribute_vertex_schemas_dict["attribute"],
            self.model_lines_attribute_vertex_prefix,
        )
        params = schemas.Attribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(
            params.id,
            params.block_ids,
            params.name,
            params.item,
            params.points,
            params.minimum,
            params.maximum,
        )
