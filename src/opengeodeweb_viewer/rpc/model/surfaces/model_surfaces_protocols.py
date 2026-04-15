# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkRenderingCore import vtkCompositePolyDataMapper

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
    deterministic_color,
)
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelSurfacesView(VtkModelView):
    model_surfaces_prefix = "opengeodeweb_viewer.model.surfaces."
    model_surfaces_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_surfaces_prefix + model_surfaces_schemas_dict["visibility"]["rpc"])
    def setModelSurfacesPolygonsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_surfaces_schemas_dict["visibility"],
            self.model_surfaces_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetBlocksVisibility(params.id, params.block_ids, params.visibility)

    @exportRpc(model_surfaces_prefix + model_surfaces_schemas_dict["color"]["rpc"])
    def setModelSurfacesColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_surfaces_schemas_dict["color"],
            self.model_surfaces_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            return
        attr = mapper.GetCompositeDataDisplayAttributes()
        for block_id in params.block_ids:
            block_ds = pipeline.blockDataSets[block_id]
            if params.color_mode == schemas.ColorMode.RANDOM:
                geode_id = pipeline.blockGeodeIds[block_id]
                r, g, b = deterministic_color(geode_id)
                attr.SetBlockColor(block_ds, [r, g, b])
            elif params.color is not None:
                r, g, b = (
                    params.color.r / 255,
                    params.color.g / 255,
                    params.color.b / 255,
                )
                attr.SetBlockColor(block_ds, [r, g, b])
        mapper.Modified()