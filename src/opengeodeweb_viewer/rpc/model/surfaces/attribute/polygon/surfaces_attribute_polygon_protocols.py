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


class VtkModelSurfacesAttributePolygonView(VtkModelView):
    model_surfaces_attribute_polygon_prefix = (
        "opengeodeweb_viewer.model.surfaces.attribute.polygon."
    )
    model_surfaces_attribute_polygon_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(
        model_surfaces_attribute_polygon_prefix
        + model_surfaces_attribute_polygon_schemas_dict["name"]["rpc"]
    )
    def setModelSurfacesPolygonAttributeName(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_surfaces_attribute_polygon_schemas_dict["name"],
            self.model_surfaces_attribute_polygon_prefix,
        )
        params = schemas.Name.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        self.displayAttributeOnCells(pipeline, params.block_ids, params.name, params.item)

    @exportRpc(
        model_surfaces_attribute_polygon_prefix
        + model_surfaces_attribute_polygon_schemas_dict["color_map"]["rpc"]
    )
    def setModelSurfacesPolygonAttributeColorMap(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_surfaces_attribute_polygon_schemas_dict["color_map"],
            self.model_surfaces_attribute_polygon_prefix,
        )
        params = schemas.ColorMap.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        self.setupColorMap(
            pipeline, params.block_ids, params.points, params.minimum, params.maximum
        )
