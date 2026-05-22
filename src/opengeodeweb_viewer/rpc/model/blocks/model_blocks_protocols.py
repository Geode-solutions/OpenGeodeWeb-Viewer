# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkRenderingCore import vtkCompositePolyDataMapper

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView, ColorResult
from . import schemas


class VtkModelBlocksView(VtkModelView):
    model_blocks_prefix = "opengeodeweb_viewer.model.blocks."
    model_blocks_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_blocks_prefix + model_blocks_schemas_dict["visibility"]["rpc"])
    def setModelBlocksPolyhedraVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_schemas_dict["visibility"],
            self.model_blocks_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetBlocksVisibility(params.id, params.block_ids, params.visibility)

    @exportRpc(model_blocks_prefix + model_blocks_schemas_dict["color"]["rpc"])
    def setModelBlocksColor(self, rpc_params: RpcParams) -> list[ColorResult]:
        validate_schema(
            rpc_params,
            self.model_blocks_schemas_dict["color"],
            self.model_blocks_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        return self.apply_color(
            pipeline, params.block_ids, params.color_mode.value, params.color
        )

    def displayAttributeOnBlocks(
        self, data_id: str, block_ids: list[int], attribute_name: str, field_type: str
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            raise Exception("Mapper is not a vtkCompositePolyDataMapper")

        attributes = mapper.GetCompositeDataDisplayAttributes()
        mapper.ScalarVisibilityOn()
        if field_type == "points":
            mapper.SetScalarModeToUsePointData()
        else:
            mapper.SetScalarModeToUseCellData()

        for block_id in block_ids:
            block_dataset = pipeline.blockDataSets[block_id]
            if block_dataset:
                if field_type == "points":
                    block_dataset.GetPointData().SetActiveScalars(attribute_name)
                else:
                    block_dataset.GetCellData().SetActiveScalars(attribute_name)
                attributes.RemoveBlockColor(block_dataset)

        mapper.Modified()

    @exportRpc(model_blocks_prefix + model_blocks_schemas_dict["attribute_name"]["rpc"])
    def setModelBlocksAttributeName(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_schemas_dict["attribute_name"],
            self.model_blocks_prefix,
        )
        params = schemas.AttributeName.from_dict(rpc_params)
        self.displayAttributeOnBlocks(
            params.id, params.block_ids, params.name, params.field_type.value
        )
        self.render(-1)

    @exportRpc(model_blocks_prefix + model_blocks_schemas_dict["attribute_color_map"]["rpc"])
    def setModelBlocksAttributeColorMap(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_schemas_dict["attribute_color_map"],
            self.model_blocks_prefix,
        )
        params = schemas.AttributeColorMap.from_dict(rpc_params)
        self.modelSetupColorMap(params.id, params.points, params.minimum, params.maximum)
        self.render(-1)

