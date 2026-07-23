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


class VtkModelBlocksAttributePolyhedronView(VtkModelView):
    model_blocks_attribute_polyhedron_prefix = (
        "opengeodeweb_viewer.model.blocks.attribute.polyhedron."
    )
    model_blocks_attribute_polyhedron_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(
        model_blocks_attribute_polyhedron_prefix
        + model_blocks_attribute_polyhedron_schemas_dict["attribute"]["rpc"]
    )
    def setModelBlocksPolyhedronAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_attribute_polyhedron_schemas_dict["attribute"],
            self.model_blocks_attribute_polyhedron_prefix,
        )
        params = schemas.Attribute.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        self.displayAttributeOnCells(pipeline, params.block_ids, params.name, params.item)
        self.setupColorMap(pipeline, params.block_ids, params.points, params.minimum, params.maximum)
